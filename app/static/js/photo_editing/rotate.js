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
            this.flipImage('horizontal');
        });

        // Flip vertical button
        this.flipVertical.addEventListener('click', () => {
            this.flipImage('vertical');
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

    // Flip the image horizontally or vertically
    flipImage(direction) {
    // Create form data for the request
    const formData = new FormData();

    // Convert current image to blob and append to form
    PhotoUtils.urlToFile(window.currentImage || window.originalImage, "image.jpg", "image/jpeg")
        .then(imageFile => {
            formData.append('image', imageFile);
            formData.append('flip_direction', direction);

            // Show loading state on the flip button that was clicked
            const flipBtn = direction === 'horizontal' ? this.flipHorizontal : this.flipVertical;
            const originalHTML = flipBtn.innerHTML;
            flipBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            flipBtn.disabled = true;

            // Send the request to the server
            fetch('/utils/flip-image', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Show the result
                    window.showResult(data.image);
                } else {
                    alert('Error: ' + (data.error || 'Unknown error flipping the image'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while flipping the image: ' + error.message);
            })
            .finally(() => {
                // Reset button state
                flipBtn.innerHTML = originalHTML;
                flipBtn.disabled = false;
            });
        })
        .catch(error => {
            console.error('Error preparing image:', error);
            alert('An error occurred while preparing the image');
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