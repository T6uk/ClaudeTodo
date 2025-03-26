// app/static/js/photo_editing/watermark.js

/**
 * Watermark functionality for photo editing
 */
class WatermarkTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');

        // Watermark controls
        this.watermarkText = document.getElementById('watermark-text');
        this.watermarkSize = document.getElementById('watermark-size');
        this.watermarkOpacity = document.getElementById('watermark-opacity');
        this.watermarkPosition = document.getElementById('watermark-position');
        this.watermarkColor = document.getElementById('watermark-color');
        this.watermarkBtn = document.getElementById('apply-watermark-btn');

        // Check if all elements exist
        if (!this.watermarkText || !this.watermarkSize || !this.watermarkOpacity ||
            !this.watermarkPosition || !this.watermarkColor || !this.watermarkBtn) {
            console.error('One or more watermark elements not found');
            return;
        }

        this.init();
    }

    init() {
        // Update size display
        this.watermarkSize.addEventListener('input', () => {
            const sizeValue = document.getElementById('watermark-size-value');
            if (sizeValue) {
                sizeValue.textContent = `${this.watermarkSize.value}px`;
            }
        });

        // Update opacity display
        this.watermarkOpacity.addEventListener('input', () => {
            const opacityValue = document.getElementById('watermark-opacity-value');
            if (opacityValue) {
                const percentage = Math.round(this.watermarkOpacity.value * 100);
                opacityValue.textContent = `${percentage}%`;
            }
        });

        // Initialize displays
        const sizeValue = document.getElementById('watermark-size-value');
        if (sizeValue) {
            sizeValue.textContent = `${this.watermarkSize.value}px`;
        }

        const opacityValue = document.getElementById('watermark-opacity-value');
        if (opacityValue) {
            const percentage = Math.round(this.watermarkOpacity.value * 100);
            opacityValue.textContent = `${percentage}%`;
        }

        // Apply watermark button handler
        this.watermarkBtn.addEventListener('click', () => {
            const text = this.watermarkText.value.trim();

            if (!text) {
                alert('Please enter watermark text');
                return;
            }

            const size = parseInt(this.watermarkSize.value) || 24;
            const opacity = parseFloat(this.watermarkOpacity.value) || 0.5;
            const position = this.watermarkPosition.value || 'bottom-right';
            const color = this.watermarkColor.value || '#ffffff';

            this.applyWatermark(text, size, opacity, position, color);
        });
    }

    // Apply watermark to the image
    applyWatermark(text, size, opacity, position, color) {
        // Create form data for the request
        const formData = new FormData();

        // Convert current image to blob and append to form
        PhotoUtils.urlToFile(window.currentImage || window.originalImage, "image.jpg", "image/jpeg")
            .then(imageFile => {
                formData.append('image', imageFile);
                formData.append('text', text);
                formData.append('size', size);
                formData.append('opacity', opacity);
                formData.append('position', position);
                formData.append('color', color);

                // Show loading state
                PhotoUtils.toggleButtonLoading(
                    this.watermarkBtn,
                    true,
                    '<i class="fas fa-copyright me-2"></i> Apply Watermark',
                    '<i class="fas fa-spinner fa-spin me-2"></i> Processing...'
                );

                // Send the request to the server
                fetch('/utils/watermark-image', {
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
                        alert('Error: ' + (data.error || 'Unknown error processing the watermark'));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while applying the watermark: ' + error.message);
                })
                .finally(() => {
                    // Reset button state
                    PhotoUtils.toggleButtonLoading(
                        this.watermarkBtn,
                        false,
                        '<i class="fas fa-copyright me-2"></i> Apply Watermark',
                        ''
                    );
                });
            })
            .catch(error => {
                console.error('Error preparing image:', error);
                alert('An error occurred while preparing the image');
            });
    }

    // Reset watermark controls
    reset() {
        if (this.watermarkText) this.watermarkText.value = '';
        if (this.watermarkSize) this.watermarkSize.value = '24';
        if (this.watermarkOpacity) this.watermarkOpacity.value = '0.5';
        if (this.watermarkPosition) this.watermarkPosition.value = 'bottom-right';
        if (this.watermarkColor) this.watermarkColor.value = '#ffffff';

        // Reset displays
        const sizeValue = document.getElementById('watermark-size-value');
        if (sizeValue) sizeValue.textContent = '24px';

        const opacityValue = document.getElementById('watermark-opacity-value');
        if (opacityValue) opacityValue.textContent = '50%';
    }
}

// Initialize the watermark tool when the window loads
window.addEventListener('load', () => {
    window.watermarkTool = new WatermarkTool();
});