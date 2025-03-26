// app/static/js/photo_editing/scale.js

/**
 * Scaling functionality for photo editing
 */
class ScaleTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');

        // Scale controls
        this.widthInput = document.getElementById('width-input');
        this.heightInput = document.getElementById('height-input');
        this.maintainAspect = document.getElementById('maintain-aspect');
        this.scaleBtn = document.getElementById('scale-btn');

        this.init();
    }

    init() {
        // Width input change
        this.widthInput.addEventListener('input', () => {
            if (this.maintainAspect.checked && window.aspectRatio) {
                const newWidth = parseInt(this.widthInput.value) || 0;
                const newHeight = Math.round(newWidth / window.aspectRatio);
                this.heightInput.value = newHeight;
            }
        });

        // Height input change
        this.heightInput.addEventListener('input', () => {
            if (this.maintainAspect.checked && window.aspectRatio) {
                const newHeight = parseInt(this.heightInput.value) || 0;
                const newWidth = Math.round(newHeight * window.aspectRatio);
                this.widthInput.value = newWidth;
            }
        });

        // Scale button handler
        this.scaleBtn.addEventListener('click', () => {
            const width = parseInt(this.widthInput.value);
            const height = parseInt(this.heightInput.value);

            if (!width || !height) {
                alert('Please enter both width and height values');
                return;
            }

            this.scaleImage(width, height);
        });
    }

    // Scale the image to the specified dimensions
    scaleImage(width, height) {
        // Create form data for the request
        const formData = new FormData();

        // Convert current image to blob and append to form
        PhotoUtils.urlToFile(window.currentImage || window.originalImage, "image.jpg", "image/jpeg")
            .then(imageFile => {
                formData.append('image', imageFile);
                formData.append('width', width);
                formData.append('height', height);
                formData.append('maintain_aspect', this.maintainAspect.checked);

                // Show loading state
                PhotoUtils.toggleButtonLoading(
                    this.scaleBtn,
                    true,
                    '<i class="fas fa-compress-arrows-alt me-2"></i> Resize Image',
                    '<i class="fas fa-spinner fa-spin me-2"></i> Processing...'
                );

                // Send the request to the server
                fetch('/utils/scale-image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update aspect ratio for the new dimensions
                        window.aspectRatio = data.width / data.height;

                        // Show the result
                        window.showResult(data.image);
                    } else {
                        alert('Error: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while processing the image');
                })
                .finally(() => {
                    // Reset button state
                    PhotoUtils.toggleButtonLoading(
                        this.scaleBtn,
                        false,
                        '<i class="fas fa-compress-arrows-alt me-2"></i> Resize Image',
                        ''
                    );
                });
            });
    }

    // Reset scale controls
    reset() {
        this.widthInput.value = '';
        this.heightInput.value = '';
        this.maintainAspect.checked = true;
    }
}

// Initialize the scale tool when the window loads
window.addEventListener('load', () => {
    window.scaleTool = new ScaleTool();
});