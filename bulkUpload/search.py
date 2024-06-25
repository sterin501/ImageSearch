#!/usr/bin/python3
from PIL import Image
import numpy as np
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.applications.resnet50 import ResNet50
from neo4j import GraphDatabase
import os,io
import base64



folder_path = 'search'
image_extensions = ['.jpg', '.jpeg', '.png', '.gif','.JPG','.JPEG','.PNG']
files = os.listdir(folder_path)

def reduce_image_file_size(image, quality=10):
    output_stream = io.BytesIO()

    # Save the image with reduced file size to the stream
    print ("Compressing")
    image.save(output_stream, format="JPEG", optimize=True, quality=quality)

    # Rewind the stream to the beginning
    output_stream.seek(0)

    # Create a new image object from the compressed data
    compressed_image = Image.open(output_stream)

    # Return the compressed image object
    return compressed_image



def createSearchVector(image_name):
    print(f"creating vector for   {image_name}")
    # Load the image
    oldimage = Image.open(folder_path + "/" + image_name)

    # Preprocess the image
    image = reduce_image_file_size(oldimage)

    image = image.convert("RGB")
    image_array = np.array(image) / 255.0

    # Vectorize the image
    model = ResNet50(weights="imagenet", include_top=False)
    features = model.predict(np.array([image_array]))
    vector = StandardScaler().fit_transform(features.reshape(-1, 2048))
    return  vector

def search(vector,algo):
  print(f"search using    {algo}")
# Store the vector in Neo4j
  driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "secret123"))
  with driver.session() as session:
      result = session.run('''CALL db.index.vector.queryNodes($algo,5,$vector)
                   YIELD node AS similarAbstract, score
                   RETURN  similarAbstract.name as name ,score order by score desc limit 5 ''',
                   vector=vector[0].tolist(),algo=algo)
      for kk in (result):
               print (f"name {kk['name']} {kk['score']}")


def base64Image(image_name):
  driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "secret123"))
  print(f"searching  {image_name}")
  base64String=""
  with driver.session() as session:
     result=session.run("match(a:Image{name:$name})-[:Compress]-> (b) RETURN b.base64 as base64",name=image_name)
     for kk in (result):
               base64String=(kk['base64'])
     
  print (base64String)
  decodeit = open('output.jpeg', 'wb')
  decodeit.write(base64.b64decode((base64String)))
  decodeit.close()



def createImage(base64Image):
    decodeit = open('output.jpeg', 'wb')
    decodeit.write(base64.b64decode((base64Image)))
    #decodeit.write(st)
    decodeit.close()


if __name__ == '__main__':

  for file in files:
    file_extension = os.path.splitext(folder_path+"/"+file)[1]
    if file_extension in image_extensions:
           searchVector=createSearchVector (file)
           search(searchVector,"imageCosine")
           search(searchVector, "imageEuclidean")


