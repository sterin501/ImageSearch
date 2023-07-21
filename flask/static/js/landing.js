$(document).ready(function(){

console.log("ss");



  var url = window.location.href;
  console.log(url);
  var parts = url.split('/');
  var filename = parts[parts.length - 3];
  var addStatus = (parts[4]);

    if (addStatus ==="True"){
                           console.log("No Button is required");
                           document.title = "Adding files";

                           checkInNeo4j(filename);

         }else{

            checkForVectorInNeo4j(filename);
            searchButton (filename);
                }

viewImage (filename);
});

function checkInNeo4j(filename){

       var Request_data={
       'filename':filename
       }


fetch('/AddImageService', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(Request_data)
})
  .then(response => response.json())
  .then(data => {

    console.log(data);
    document.getElementById("VectorStatus").innerHTML = "<strong>Vector Created:</strong> Yes";
    document.getElementById("ImageInDatabase").innerHTML = "<strong>Image added successfully in neo4j:</strong> Yes";
    document.title = "Image added ";


  })
  .catch(error => {

    console.error(error);
  });




}


function checkForVectorInNeo4j(filename)
{

       var Request_data={
       'filename':filename
       }


fetch('/checkForVector', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(Request_data)
})
  .then(response => response.json())
  .then(data => {

    console.log(data);
    document.getElementById("VectorStatus").innerHTML = "<strong>Vector Created:</strong> Yes";


  })
  .catch(error => {

    console.error(error);
  });


}// end of function


function viewImage (filename)
{

  var imgContainer = $('<div>').addClass('image-container');
  var img = $('<img>').attr('src', '/view/' + filename).attr('alt', 'Image');
  imgContainer.append(img);
  //$('body').append(imgContainer);
  $('#ImageView').append(imgContainer);

}


function searchButton (filename)

{



  $('#AlgoSelect').show();
  $('#SearchButton').show();
  //  var button = $('<button>').text('Search Image');
  // $('body').append(button);
  // console.log(filename);
   $('#SearchButton').click(function() {
       var AlgoSelect=$("#AlgoSelect").find(":selected").val();
       var Request_data={
       'filename':filename,
       'algo':AlgoSelect
       }
          var dialog = $('<div>').text('Searching in Neo4j using  '+AlgoSelect);
        dialog.dialog({
            modal: true,
            title: 'Search Status',
            closeOnEscape: false,
            draggable: false,
            resizable: false
        });
      fetch('/searchImage',{
      method: 'POST',
           headers: {
          'Content-Type': 'application/json'
              },
      body: JSON.stringify(Request_data)
      })
  .then(response => response.json())
  .then(data => {
    // Handle the API response data
    console.log(data);
    $('#imageResult').empty();
    dialog.dialog('close');
    $('body').append("<br>   "+AlgoSelect + " "+data['timerequired'] + "sec");
    data['neo4jresult'].forEach(function(obj) {
    imgContainer=render_image(obj.base64,obj.similarity,obj.descr);
    $('#imageResult').append(imgContainer);
});
  })
  .catch(error => {
    console.error(error);
  });
  });


}


function render_image(base64Object,similarity,descr)

{

//console.log(base64Object);
var base64Image = "data:image/jpg;base64,"+base64Object;  // Replace with your base64-encoded image data

//var img = document.createElement('img');
   // img = $('<div>').addClass('image-container');

     var imgContainer = $('<div>').addClass('image-container');
     var img = $('<img>').attr('src', base64Image).attr('alt', 'Image');
     var description = $('<div>').addClass('image-description').text(descr+" "+similarity);

      imgContainer.append(img);
      imgContainer.append(description);
      imgContainer.hover(
  function() {
    description.css('visibility', 'visible').css('opacity', '1');
  },
  function() {
    description.css('visibility', 'hidden').css('opacity', '0');
  }
);

return imgContainer;

}