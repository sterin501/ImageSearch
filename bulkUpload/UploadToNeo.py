#!/usr/bin/python3
from PIL import Image
import numpy as np
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.applications.resnet50 import ResNet50
from neo4j import GraphDatabase
import os,io
import base64
import shutil


folder_path = 'upload'
image_extensions = ['.jpg', '.jpeg', '.png', '.gif','.JPG','.JPEG','.PNG']
files = os.listdir(folder_path+"/images")

def reduce_image_file_size(image, quality=10):
    output_stream = io.BytesIO()

    # Save the image with reduced file size to the stream
    print ("Compressing")
    image.save(output_stream, format="JPEG", optimize=True, quality=quality)

    # Rewind the stream to the beginning
    output_stream.seek(0)

    # Create a new image object from the compressed data
    


    # Return the compressed image object
    print (type(output_stream))
    
    return output_stream





def upload(image_name):

# Load the image
 try:
  oldimage = Image.open(folder_path+"/images/"+image_name)
  file_size = os.path.getsize(folder_path+"/images/"+image_name)
  print(f"File size: {file_size} bytes")
  width, height = oldimage.size
  print(f"Image size: {width} x {height}")
  desc_file=os.path.splitext(image_name)[0] + ".txt"
  with open(folder_path+"/desc/"+desc_file, 'r') as file:
    desc = file.read()


# Preprocess the image
  #image = image.resize((224, 224))
  output_stream = reduce_image_file_size(oldimage)
  compressed_image = Image.open(output_stream)
  #width, height = compressed_image.size
  #print(f"Image size: {width} x {height}")
  
  #exit (0)
  image = compressed_image.convert("RGB")
  image_array = np.array(image) / 255.0

# Vectorize the image
  model = ResNet50(weights="imagenet", include_top=False)
  features = model.predict(np.array([image_array]))
  vector = StandardScaler().fit_transform(features.reshape(-1, 2048))

# Storing original image as base64
  with open(folder_path+"/images/"+image_name, "rb") as image2string:
          converted_string = base64.b64encode(image2string.read())

# compressed for display
  #compressed_image_bytes = compressed_image.tobytes()
  compressed_base64_str = base64.b64encode(output_stream.getvalue())

# Store the vector in Neo4j
  driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "secret123"))
  print(f"uploading {image_name}")
  with driver.session() as session:
      result=session.run(''' CREATE (I:Image {name: $name,desc:$desc})-[:Original]->(:Originalbase64 {base64:$base64})
                             CREATE (I)-[:Compress]-> (:Compress{base64:$compressed_base64_str})  
                             WITH I 
                             CALL db.create.setNodeVectorProperty(I, "vectorCosine", $vector)
                             CALL db.create.setNodeVectorProperty(I, "vectorEuclidean", $vector)
                             ''',
                             name=image_name,desc=desc,vector=vector[0].tolist(),base64=converted_string,compressed_base64_str=compressed_base64_str)
      if (result.consume().counters.contains_updates):
                 print(result.consume().counters)
  shutil.move(folder_path+"/images/"+image_name, folder_path+"/images/done")
 except FileNotFoundError:
    print ("File not found")

if __name__ == '__main__':
  for file in files:
    print (file)
    file_extension = os.path.splitext(folder_path+"/images/"+file)[1]
    if file_extension in image_extensions:
       upload (file)
