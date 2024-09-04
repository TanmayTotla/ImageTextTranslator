document.addEventListener("DOMContentLoaded", function() {
    // Get the form and other elements
    const uploadForm = document.getElementById("upload-form");
    const resultImage = document.getElementById("translatedImage");
    const loader = document.getElementById("loader");

    // Form submission handler
    uploadForm.onsubmit = function(event) {
        event.preventDefault();  // Prevent default form submission

        // Show the loader while processing
        loader.style.display = "block";

        // Get form data
        const formData = new FormData(this);

        // Send the form data to the server
        fetch('/process', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error processing the image.");
            }
            return response.blob();  // Get response as a blob (image)
        })
        .then(blob => {
            // Create an object URL for the blob and display the image
            const url = URL.createObjectURL(blob);
            resultImage.src = url;
            resultImage.style.display = "block";  // Show the translated image
        })
        .catch(error => {
            console.error('Error processing the image:', error);
            alert('There was an error processing the image. Please try again.');
        })
        .finally(() => {
            // Hide the loader when done
            loader.style.display = "none";
        });
    };
});