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

def doSearch(image_name):                         ## Doing Search

  checkForVectorAndCreate(image_name)
  print(f"searching  {image_name}")
  neo4jresult=[]
  with driver.session() as session:
      #result=session.run("match(a:Image) with a, gds.similarity.cosine(a.vector, $vector) as similarity return a.name as name,a.base64 as base64 order by similarity desc limit 1  ",vector=vector[0].tolist())
      result=session.run('''CALL {
                   MATCH (a:SearchImage{name:$name}) RETURN a.vector as Searchvector
    }
      MATCH (a:Image)-[:Compress]-> (b) with a,b, gds.similarity.cosine(a.vector, Searchvector) as similarity 
      RETURN a.desc as desc, a.name as name, similarity as similarity,b.base64 as base64 order by similarity desc limit 5 '''
                         ,name=image_name)


      for kk in (result):
               print (f"name {kk['name']} {kk['similarity']}")
               string_data = kk['base64'].decode('utf-8')
               neo4jresult.append({'descr':kk['desc'],'neo4jname':kk['name'],'similarity':kk['similarity'],'base64':string_data})

  return (neo4jresult)

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
            result = session.run(''' MATCH (I:Image {name: $name}) SET I.vector=$vector
                                     MERGE (I)-[:Compress]-> (:Compress{base64:$compressed_base64_str})
                                     RETURN I  ''',
                                 name=filename, vector=vector[0].tolist(),compressed_base64_str=compressed_base64_str)
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

  return (neo4jresult)

