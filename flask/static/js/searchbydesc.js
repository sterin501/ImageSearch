$(document).ready(function(){

console.log("searchPage");



 $("#searchInputButton").click(function() {
console.log("clicked");
//removeImages()
sendJson()
 }); // end of button



}); // end of ready


function removeImages(){


//var imageContainers = document.getElementsByClassName("image-container");
//for (var i = 0; i < imageContainers.length; i++) {
//  var imageElement = imageContainers[i].querySelector("img");
//  if (imageElement) {
//    imageElement.empty();
//  }
//}


}

function sendJson()
{

var searchWord = document.getElementById("searchInput").value;
    console.log("Search word: " + searchWord);
    Request_data={"word":document.getElementById("searchInput").value}


      fetch('/searchByDesc',{
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
    $('#imageResult').empty();  // To clear the old results

    $('body').append("<br> Results </br>");

    data.forEach(function(obj) {
    imgContainer=render_image(obj.base64,obj.similarity,obj.descr);
    $('#imageResult').append(imgContainer);
                                });


  })
  .catch(error => {
    console.error(error);
  });


}

function viewImage (filename)
{

  var imgContainer = $('<div>').addClass('image-container');
  var img = $('<img>').attr('src', '/view/' + filename).attr('alt', 'Image');
  imgContainer.append(img);
  $('body').append(imgContainer);

}


function render_image(base64Object,similarity,descr)

{

     var base64Image = "data:image/jpg;base64,"+base64Object;  // Replace with your base64-encoded image data
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

 // $('body').append(imgContainer);
 return imgContainer;

}