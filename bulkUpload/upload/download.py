#!/usr/bin/python3
import csv
import requests
from neo4j import GraphDatabase

search_word='sambar'
csv_file = 'images_full.csv'

def inNeo4j(name):
    data_base_connection = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "secret123"))
    with data_base_connection.session() as session:
       query = "match(a:Image{name:$name}) RETURN a.name as name"
       result = session.run(query, name=name)
       for kk in (result):
          return True
       else:
          return False


def download_image(image_url, save_path):
      
   try:
     response = requests.get(image_url, stream=True)
     if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
   except Exception as e:
    # Handling code for any type of error
      print("An error occurred:", e)


def process_csv(csv_file):
    count=0
    rowcount=0
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            image_id = row['ImageID']
            rowcount+=1
            print (f"\r row count {rowcount}",end="   _  ")
            if search_word in row['Title']:
               print (row['Title'])
               if inNeo4j(image_id):
                  continue
               image_url = row['OriginalURL']
               print (row['OriginalSize'])
            ### ImageID,Subset,OriginalURL,OriginalLandingURL,License,AuthorProfileURL,Author,Title,OriginalSize,OriginalMD5,Thumbnail300KURL
               if (int (row['OriginalSize']) < 933185):
                 save_path = f'images/{image_id}.jpg'  # Modify the save path as per your requirement
                 download_image(image_url, save_path)
                 print(f"Downloaded image: {image_id}")
                 with open(f'desc/{image_id}.txt', 'w') as file:
                      file.write(row['Title'])
                 count+=1
                 print(f"count {count}")
               else:
                  print (f"Skipping due to {row['OriginalSize']} ")



# Example usage

process_csv(csv_file)
