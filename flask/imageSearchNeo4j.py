#!/usr/bin/python3
from PIL import Image
import numpy as np
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.applications.resnet50 import ResNet50
from neo4j import GraphDatabase
import os,io
import base64



driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "secret123"))
def reduce_image_file_size(image, quality=10):            ## For creating vector with 10% size
    try:
        output_stream = io.BytesIO()

    # Save the image with reduced file size to the stream
        print ("Compressing")
        image.save(output_stream, format="JPEG", optimize=True, quality=quality)

    # Rewind the stream to the beginning
        output_stream.seek(0)
        return output_stream
    except:
        rgb_image = image.convert("RGB")
        rgb_image.save(output_stream,format="JPEG")
        output_stream.seek(0)
        return output_stream



def checkForVectorAndCreate(image_name):                  ## Create Vector for input image

    session = driver.session()
    query = "match(a:SearchImage{name:$name}) RETURN a.name as name"
    result = session.run(query, name=image_name)
    for kk in (result):
      print (kk)
      return {"status": "ok"}

    else:
      print ("Not created .Creating search vector")

    oldimage = Image.open("upload/" + image_name)

    # Preprocess the image
    output_stream = reduce_image_file_size(oldimage)
    image = Image.open(output_stream)

    image = image.convert("RGB")
    image_array = np.array(image) / 255.0
    model = ResNet50(weights="imagenet", include_top=False)
    features = model.predict(np.array([image_array]))
    vector = StandardScaler().fit_transform(features.reshape(-1, 2048))
    print(f"uploading {image_name}")
    with driver.session() as session:
         result=session.run(''' MERGE (I:SearchImage {name: $name,vector: $vector})
                             RETURN I  ''',
                             name=image_name,vector=vector[0].tolist())
         if (result.consume().counters.contains_updates):
                 print(result.consume().counters)
    return {"status": "ok","Created":True}

def doSearch(image_name,algo):                         ## Doing Search

  checkForVectorAndCreate(image_name)
  print(f"searching  {image_name}")
  neo4jresult=[]
  query='''MATCH (a:SearchImage{name: $name})
WITH a.vector as Searchvector
CALL {
    WITH Searchvector
    CALL db.index.vector.queryNodes($algo, 5, Searchvector)
    YIELD node AS similarAbstract, score
    RETURN collect({name: similarAbstract.name, score: score,desc:similarAbstract.desc}) AS results   
}
UNWIND results AS result
MATCH (i:Image {name: result.name})-[:Compress]->(b)
RETURN b.base64  as base64 , result.name AS name, result.score AS similarity ,result.desc as desc
ORDER BY result.score DESC
LIMIT 5

'''
  with driver.session() as session:
      result=session.run(query,name=image_name,algo=algo)
      for kk in (result):
               print (f"name {kk['name']} {kk['similarity']}")
               string_data = kk['base64'].decode('utf-8')
               neo4jresult.append({'descr':kk['desc'],'neo4jname':kk['name'],'similarity':kk['similarity'],'base64':string_data})

      result_summary = result.consume()
      timerequired=(result_summary.result_consumed_after/1000)
      imageResult={'neo4jresult':neo4jresult,'timerequired':timerequired}
  return (imageResult)

def addToNeo4j(filename,converted_string,desc,vector):  ## Upload with or with our vector
    if vector:
        oldimage = Image.open("upload/" + filename)

        # Preprocess the image
        output_stream = reduce_image_file_size(oldimage)
        image = Image.open(output_stream)

        image = image.convert("RGB")
        image_array = np.array(image) / 255.0
        model = ResNet50(weights="imagenet", include_top=False)
        features = model.predict(np.array([image_array]))
        vector = StandardScaler().fit_transform(features.reshape(-1, 2048))
        compressed_base64_str = base64.b64encode(output_stream.getvalue())
        with driver.session() as session:
            result = session.run(''' MERGE (I:Image {name: $name})
                                     MERGE (I)-[:Compress]-> (:Compress{base64:$compressed_base64_str})  
                             WITH I 
                             CALL db.create.setNodeVectorProperty(I, "vectorCosine", $vector)
                             CALL db.create.setNodeVectorProperty(I, "vectorEuclidean", $vector)
                             ''',name=filename, vector=vector[0].tolist(),compressed_base64_str=compressed_base64_str)
            if (result.consume().counters.contains_updates):
                print(result.consume().counters)

        return {"status": "ok", "Created": True}

    else:
        with driver.session() as session:
            result = session.run(''' CREATE (I:Image {name: $name,desc:$desc})-[:Original]->(:Originalbase64 {base64:$base64})
                                  ''',name=filename, desc=desc, base64=converted_string)
            if (result.consume().counters.contains_updates):
                print(result.consume().counters)
        return ({'status': 'Original file in Database.'})

    return ({'status':'done'})

def doSearchByDesc(word):

  neo4jresult=[]
  with driver.session() as session:
      #result=session.run("match(a:Image) with a, gds.similarity.cosine(a.vector, $vector) as similarity return a.name as name,a.base64 as base64 order by similarity desc limit 1  ",vector=vector[0].tolist())
      result=session.run('''
      MATCH (a:Image)-[:Compress]-> (b)
      WHERE a.desc IS NOT NULL
      WITH a,b, apoc.text.sorensenDiceSimilarity($word, a.desc) AS similarity
      RETURN a.desc as desc, similarity as similarity,b.base64 as base64 order by similarity desc limit 5 '''
                         ,word=word)


      for kk in (result):
               print (f"desc {kk['desc']} {kk['similarity']}")
               string_data = kk['base64'].decode('utf-8')
               neo4jresult.append({'descr':kk['desc'],'similarity':kk['similarity'],'base64':string_data})
      result_summary = result.consume()
      timerequired=(result_summary.result_consumed_after/1000)
      imageResult={'neo4jresult':neo4jresult,'timerequired':timerequired}

  return (imageResult)

