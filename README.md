# ImageSearch

This is demo to upload image and create image vector in the neo4j database .

Later vector is used for image search


Flow :
____________


Images convert to vector using tensorflow and store as property in neo4j. This vector is used for gds.similarity.cosine procedure
This will return images based on the score .

Website based on flask can be used to add images and search 
There is different script for downloading images from internet and upload to neo4j 


Configration in Neo4j 
____________

Neo4j version : 5.6.0
Install GDS : neo4j-graph-data-science-2.4.0.jar

Install APOC : apoc-5.6.0-core.jar,apoc-5.6.0-extended.jar

Indexes can be created for image,desc property of Image label 


Configration for Flask website 
____________

1. pip install -r requirment.txt
   
2 .export FLASK_APP=app.py
3. flask run

4. Edit ImageSearchNeo4j.py with correct neo4j connection string 


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


