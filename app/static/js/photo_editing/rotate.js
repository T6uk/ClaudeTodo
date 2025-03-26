// app/static/js/photo_editing/rotate.js

/**
 * Rotation functionality for photo editing
 */
class RotateTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');

        // Rotation controls
        this.rotateLeft = document.getElementById('rotate-left');
        this.rotateRight = document.getElementById('rotate-right');
        this.flipHorizontal = document.getElementById('flip-horizontal');
        this.flipVertical = document.getElementById('flip-vertical');
        this.angleInput = document.getElementById('angle-input');
        this.angleSlider = document.getElementById('angle-slider');
        this.rotateBtn = document.getElementById('rotate-btn');

        this.init();
    }

    init() {
        // Rotate left button
        this.rotateLeft.addEventListener('click', () => {
            this.angleInput.value = -90;
            this.angleSlider.value = -90;
            this.rotateImage(-90);
        });

        // Rotate right button
        this.rotateRight.addEventListener('click', () => {
            this.angleInput.value = 90;
            this.angleSlider.value = 90;
            this.rotateImage(90);
        });

        // Flip horizontal button
        this.flipHorizontal.addEventListener('click', () => {
            // Send to server for flipping horizontally
            // This is a placeholder for future implementation
            alert('Horizontal flip will be implemented soon');
        });

        // Flip vertical button
        this.flipVertical.addEventListener('click', () => {
            // Send to server for flipping vertically
            // This is a placeholder for future implementation
            alert('Vertical flip will be implemented soon');
        });

        // Angle input change
        this.angleInput.addEventListener('input', () => {
            this.angleSlider.value = this.angleInput.value;
        });

        // Angle slider change
        this.angleSlider.addEventListener('input', () => {
            this.angleInput.value = this.angleSlider.value;
        });

        // Rotate button handler
        this.rotateBtn.addEventListener('click', () => {
            const angle = parseInt(this.angleInput.value) || 0;
            this.rotateImage(angle);
        });
    }

    // Rotate the image by the specified angle
    rotateImage(angle) {
        // Create form data for the request
        const formData = new FormData();

        // Convert current image to blob and append to form
        PhotoUtils.urlToFile(window.currentImage || window.originalImage, "image.jpg", "image/jpeg")
            .then(imageFile => {
                formData.append('image', imageFile);
                formData.append('angle', angle);

                // Show loading state
                PhotoUtils.toggleButtonLoading(
                    this.rotateBtn,
                    true,
                    '<i class="fas fa-sync-alt me-2"></i> Apply Rotation',
                    '<i class="fas fa-spinner fa-spin me-2"></i> Processing...'
                );

                // Send the request to the server
                fetch('/utils/rotate-image', {
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
                        this.rotateBtn,
                        false,
                        '<i class="fas fa-sync-alt me-2"></i> Apply Rotation',
                        ''
                    );
                });
            });
    }

    // Reset rotation controls
    reset() {
        this.angleInput.value = 0;
        this.angleSlider.value = 0;
    }
}

// Initialize the rotate tool when the window loads
window.addEventListener('load', () => {
    window.rotateTool = new RotateTool();
});