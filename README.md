# ImageSearch

This is demo to upload image and create image vector in the neo4j database .

Later vector is used for image search

____________

Flow :
____________


We convert images to vectors using TensorFlow and store these vectors as properties in Neo4j.

By utilizing Neo4j's vector index feature, we can run cosine similarity algorithms on these vectors to find similarities.

Additionally, a website built on Flask can be used to upload images and perform searches based on these vectors.

____________


There is different script for downloading images from internet and upload to neo4j 

____________

Configration in Neo4j 
____________

Neo4j version : 5.20.0

Install APOC : apoc-5.20.0-core.jar

Create vector index

```
CALL db.index.vector.createNodeIndex('imageCosine', 'Image', 'vectorCosine', 2048, 'cosine');
```
```
CALL db.index.vector.createNodeIndex('imageEuclidean', 'Image', 'vectorEuclidean', 2048, 'euclidean'); // Optional 
```
____________

Configration for Flask website 
____________

  1.  pip install -r requirment.txt
  2.  export FLASK_APP=app.py  
  3.  flask run --port 5002                  
  4.  Edit ImageSearchNeo4j.py with correct neo4j connection string 


____________
Bulk download and upload of images 
____________


To download use : ImageSearch/bulkUpload/upload/download.py 

This will read images_full.csv and download as per that . 

To get csv : https://storage.googleapis.com/openimages/2016_08/images_2016_08_v5.tar.gz


To upload to Neo4j : ImageSearch/bulkUpload/UploadToNeo.py

This will upload images to neo4j . Edit the connection string for neo4j connection 

____________

For better performance to create image vector install CUDS drivers 

https://developer.nvidia.com/cuda-downloads

____________

Cypher to upload image vector

```
CREATE (I:Image {name: $name,desc:$desc})-[:Original]->(:Originalbase64 {base64:$base64})
CREATE (I)-[:Compress]-> (:Compress{base64:$compressed_base64_str})  
WITH I 
CALL db.create.setNodeVectorProperty(I, "vectorCosine", $vector)
```
____________

Cypher to search image vector

```
CALL db.index.vector.queryNodes('imageCosine', 5, $vector)
YIELD node AS similarAbstract, score
RETURN  similarAbstract.name,score
```          
                             

