import json

from flask import Flask, render_template, request,url_for,redirect,send_from_directory
import os
from PIL import Image
import uuid
import base64
from imageSearchNeo4j import doSearch,checkForVectorAndCreate,doSearchByDesc,addToNeo4j


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])   ## Home page will redirect to upload
def homepage():
    return redirect("/upload")

@app.route('/upload', methods=['GET', 'POST'])  ## Upload for seaching
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename.replace(' ', '_')
            unique_prefix = str(uuid.uuid4().hex)[:6]
            filename=unique_prefix+filename
            file.save(os.path.join('upload', filename))
            image = Image.open('upload/'+filename)
            image_size = os.path.getsize('upload/'+filename)
            image_resolution = f"{image.width}x{image.height}"
        return redirect(url_for('landing',add=False,filename=filename,image_size=image_size, image_resolution=image_resolution))
    return render_template('upload.html')

@app.route('/addImage', methods=['GET', 'POST'])   ## adding new Image to neo4j
def addImage():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename.replace(' ', '_')
            unique_prefix = str(uuid.uuid4().hex)[:6]
            filename=unique_prefix+filename
            file.save(os.path.join('upload', filename))
            image = Image.open('upload/'+filename)
            image_size = os.path.getsize('upload/'+filename)
            image_resolution = f"{image.width}x{image.height}"
            desc = request.form.get('desc')
            print (desc)
            with open('upload/'+filename, "rb") as image2string:
                converted_string = base64.b64encode(image2string.read())
            addToNeo4j(filename=filename,converted_string=converted_string,desc=desc,vector=False)

        return redirect(url_for('landing',add=True,filename=filename,image_size=image_size, image_resolution=image_resolution))
    return render_template('addImage.html')



@app.route('/landing/<add>/<filename>/<image_size>/<image_resolution>')
def landing(add,filename,image_size,image_resolution):
    print (filename)
    return render_template('landing.html',add=add,filename=filename,image_size=image_size, image_resolution=image_resolution)

@app.route('/view/<filename>')           ## for static view
def uploaded_file(filename):
    return send_from_directory('upload', filename)


@app.route('/searchImage', methods=['POST'])                 ## Doing Image search
def searchImage():
    data = request.get_json()  # Retrieve the JSON data sent from JavaScript
    print (data)
    neo4jresult=doSearch(data['filename'])
    return json.dumps(neo4jresult)

@app.route('/checkForVector', methods=['POST'])                  ## Checking for vector in database
def checkForVector():
    data = request.get_json()  # Retrieve the JSON data sent from JavaScript
    print (data)
    vectorStatus=checkForVectorAndCreate(data['filename'])
    print (vectorStatus)
    return json.dumps(vectorStatus)


@app.route('/searchPage')                                         ## Static HTML page
def searchPage():
    data = request.get_json()  # Retrieve the JSON data sent from JavaScript
    print (data)
    #vectorStatus=checkForVectorAndCreate(data['filename'])
    #print (vectorStatus)
    return render_template('searchbydesc.html')

@app.route('/searchByDesc', methods=['POST'])                                 ## Search Description
def searchByDesc():
    data = request.get_json()  # Retrieve the JSON data sent from JavaScript
    print (data)
    neo4jResult=doSearchByDesc(data['word'])
    #print (neo4jResult)
    return json.dumps(neo4jResult)


@app.route('/AddImageService', methods=['POST'])                                        ## Adding image to neo4j
def AddImageService():
    data = request.get_json()  # Retrieve the JSON data sent from JavaScript
    print (data)
    neo4jResult=addToNeo4j(filename=data['filename'],converted_string=False,desc=False,vector=True)
    #print (neo4jResult)
    return json.dumps(neo4jResult)

if __name__ == '__main__':
    app.run()

