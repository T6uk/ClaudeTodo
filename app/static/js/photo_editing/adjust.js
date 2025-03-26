// app/static/js/photo_editing/adjust.js

/**
 * Enhanced adjustment functionality for photo editing with live preview
 */
class AdjustTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');

        // Adjustment controls
        this.brightnessSlider = document.getElementById('brightness-slider');
        this.contrastSlider = document.getElementById('contrast-slider');
        this.saturationSlider = document.getElementById('saturation-slider');
        this.sharpnessSlider = document.getElementById('sharpness-slider');

        this.brightnessValue = document.getElementById('brightness-value');
        this.contrastValue = document.getElementById('contrast-value');
        this.saturationValue = document.getElementById('saturation-value');
        this.sharpnessValue = document.getElementById('sharpness-value');

        this.adjustBtn = document.getElementById('adjust-btn');
        this.resetAdjustBtn = document.getElementById('reset-adjust-btn');

        // Keep track of original image
        this.originalImageSrc = null;

        // Preview canvas
        this.previewCanvas = document.createElement('canvas');
        this.previewCtx = this.previewCanvas.getContext('2d');

        // Debounce timer
        this.debounceTimer = null;

        this.init();
    }

    init() {
        // Initialize slider displays
        this.updateSliderDisplay(this.brightnessSlider, this.brightnessValue);
        this.updateSliderDisplay(this.contrastSlider, this.contrastValue);
        this.updateSliderDisplay(this.saturationSlider, this.saturationValue);
        this.updateSliderDisplay(this.sharpnessSlider, this.sharpnessValue);

        // Add event listeners to sliders for real-time preview
        this.brightnessSlider.addEventListener('input', () => {
            this.updateSliderDisplay(this.brightnessSlider, this.brightnessValue);
            this.updateLivePreview();
        });

        this.contrastSlider.addEventListener('input', () => {
            this.updateSliderDisplay(this.contrastSlider, this.contrastValue);
            this.updateLivePreview();
        });

        this.saturationSlider.addEventListener('input', () => {
            this.updateSliderDisplay(this.saturationSlider, this.saturationValue);
            this.updateLivePreview();
        });

        this.sharpnessSlider.addEventListener('input', () => {
            this.updateSliderDisplay(this.sharpnessSlider, this.sharpnessValue);
            this.updateLivePreview();
        });

        // Reset adjustments
        if (this.resetAdjustBtn) {
            this.resetAdjustBtn.addEventListener('click', () => {
                this.resetAdjustments();
                this.updateLivePreview();
            });
        }

        // Apply adjustments button
        this.adjustBtn.addEventListener('click', () => {
            this.applyAdjustments();
        });

        // Listen for tool activation
        document.addEventListener('toolActivated', (e) => {
            if (e.detail.tool === 'adjust') {
                this.initializePreview();
            }
        });

        // Listen for when the image is loaded
        document.addEventListener('imageLoaded', () => {
            if (window.currentTool === 'adjust') {
                this.initializePreview();
            }
        });
    }

    // Update slider display value
    updateSliderDisplay(slider, valueElement) {
        valueElement.textContent = parseFloat(slider.value).toFixed(2);
    }

    // Initialize preview
    initializePreview() {
        // Store the original image state when the tool is activated
        this.originalImageSrc = window.currentImage || window.originalImage;

        // Reset any previous filters
        this.imagePreview.style.filter = 'none';
    }

    // Update live preview using CSS filters
    updateLivePreview() {
        clearTimeout(this.debounceTimer);

        this.debounceTimer = setTimeout(() => {
            const brightness = this.brightnessSlider.value;
            const contrast = this.contrastSlider.value;
            const saturation = this.saturationSlider.value;

            // Apply CSS filters for immediate preview
            let filterString = `brightness(${brightness}) contrast(${contrast}) saturate(${saturation})`;

            // For sharpness, we can't use a CSS filter directly, but we can simulate it a bit with contrast
            if (this.sharpnessSlider.value > 1) {
                // Simulate sharpness with a slight contrast increase
                const sharpnessEffect = (this.sharpnessSlider.value - 1) * 0.2;
                filterString += ` contrast(${1 + sharpnessEffect})`;
            }

            this.imagePreview.style.filter = filterString;
        }, 30); // Small delay for better performance during slider drags
    }

    // Reset all adjustment controls
    resetAdjustments() {
        this.brightnessSlider.value = 1;
        this.contrastSlider.value = 1;
        this.saturationSlider.value = 1;
        this.sharpnessSlider.value = 1;

        this.updateSliderDisplay(this.brightnessSlider, this.brightnessValue);
        this.updateSliderDisplay(this.contrastSlider, this.contrastValue);
        this.updateSliderDisplay(this.saturationSlider, this.saturationValue);
        this.updateSliderDisplay(this.sharpnessSlider, this.sharpnessValue);

        // Reset the image preview to its original state
        this.imagePreview.style.filter = 'none';
    }

    // Apply adjustments on the server for final result
    applyAdjustments() {
        // Create form data for the request
        const formData = new FormData();

        // Convert current image to blob and append to form
        PhotoUtils.urlToFile(this.originalImageSrc, "image.jpg", "image/jpeg")
            .then(imageFile => {
                formData.append('image', imageFile);
                formData.append('brightness', this.brightnessSlider.value);
                formData.append('contrast', this.contrastSlider.value);
                formData.append('saturation', this.saturationSlider.value);
                formData.append('sharpness', this.sharpnessSlider.value);

                // Show loading state
                PhotoUtils.toggleButtonLoading(
                    this.adjustBtn,
                    true,
                    '<i class="fas fa-sliders-h me-2"></i> Apply Adjustments',
                    '<i class="fas fa-spinner fa-spin me-2"></i> Processing...'
                );

                // Send the request to the server
                fetch('/utils/adjust-image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Reset filter on preview
                        this.imagePreview.style.filter = 'none';

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
                        this.adjustBtn,
                        false,
                        '<i class="fas fa-sliders-h me-2"></i> Apply Adjustments',
                        ''
                    );
                });
            });
    }

    // Clean up when switching tools
    reset() {
        // Reset the sliders to default values
        this.resetAdjustments();

        // Clear any filter styles
        this.imagePreview.style.filter = 'none';

        // Clear the original image reference
        this.originalImageSrc = null;
    }
}

// Initialize the adjust tool when the window loads
window.addEventListener('load', () => {
    window.adjustTool = new AdjustTool();
});