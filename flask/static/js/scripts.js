// script.js

window.addEventListener('DOMContentLoaded', (event) => {



    const fileInput = document.querySelector('input[type="file"]');

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        const fileExtension = getFileExtension(file.name);

        if (!isImage(fileExtension)) {
            alert('Only image files are allowed!');
            event.target.value = '';  // Clear the file input
        }
    });

    function getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }

    function isImage(extension) {
        const imageExtensions = ['jpg', 'jpeg', 'png', 'gif'];
        return imageExtensions.includes(extension);
    }
});
