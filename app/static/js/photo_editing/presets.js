// app/static/js/photo_editing/presets.js

/**
 * Presets functionality for photo editing
 */
class PresetsTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');

        // Presets elements
        this.presetItems = document.querySelectorAll('.preset-item');
        this.applyPresetBtn = document.getElementById('apply-preset-btn');

        // Currently selected preset
        this.selectedPreset = null;

        // Original image reference
        this.originalImageSrc = null;

        this.init();
    }

    init() {
        // Initialize preset selection
        this.presetItems.forEach(item => {
            item.addEventListener('click', () => {
                // Deselect all presets
                this.presetItems.forEach(p => p.classList.remove('active'));

                // Select the clicked preset
                item.classList.add('active');
                this.selectedPreset = item.getAttribute('data-preset');

                // Preview the preset effect
                this.previewPreset(this.selectedPreset);
            });
        });

        // Apply preset button
        this.applyPresetBtn.addEventListener('click', () => {
            if (this.selectedPreset) {
                this.applyPreset(this.selectedPreset);
            } else {
                alert('Please select a preset first');
            }
        });

        // Listen for tool activation
        document.addEventListener('toolActivated', (e) => {
            if (e.detail.tool === 'presets') {
                this.initializePresets();
            }
        });

        // Listen for image loaded
        document.addEventListener('imageLoaded', () => {
            this.originalImageSrc = window.originalImage;
            if (window.currentTool === 'presets') {
                this.initializePresets();
            }
        });
    }

    // Initialize presets with the current image
    initializePresets() {
        this.originalImageSrc = window.currentImage || window.originalImage;

        // Reset selection
        this.presetItems.forEach(p => p.classList.remove('active'));
        this.selectedPreset = null;

        // Reset preview
        this.imagePreview.style.filter = 'none';
    }

    // Preview a preset using CSS filters
    previewPreset(preset) {
        // Apply CSS filter for immediate preview
        const cssFilter = this.getPresetCssFilter(preset);
        this.imagePreview.style.filter = cssFilter;
    }

    // Apply the selected preset (server-side)
    applyPreset(preset) {
        // Create form data for the request
        const formData = new FormData();

        // Convert original image to blob and append to form
        PhotoUtils.urlToFile(this.originalImageSrc || window.originalImage, "image.jpg", "image/jpeg")
            .then(imageFile => {
                formData.append('image', imageFile);
                formData.append('preset', preset);

                // Show loading state
                PhotoUtils.toggleButtonLoading(
                    this.applyPresetBtn,
                    true,
                    '<i class="fas fa-magic me-2"></i> Apply Preset',
                    '<i class="fas fa-spinner fa-spin me-2"></i> Processing...'
                );

                // Send the request to the server
                fetch('/utils/apply-preset', {
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
                        this.applyPresetBtn,
                        false,
                        '<i class="fas fa-magic me-2"></i> Apply Preset',
                        ''
                    );
                });
            });
    }

    // Get CSS filter string for preview
    getPresetCssFilter(preset) {
        switch(preset) {
            case 'vintage':
                return 'sepia(0.5) contrast(1.1) brightness(1.05) saturate(0.65)';
            case 'blackwhite':
                return 'grayscale(1) contrast(1.2) brightness(1.05)';
            case 'warm':
                return 'sepia(0.3) saturate(1.3) contrast(1.1) brightness(1.1)';
            case 'cool':
                return 'saturate(0.8) contrast(1.1) brightness(1.1) hue-rotate(180deg)';
            case 'sharp':
                return 'contrast(1.5) brightness(0.9) saturate(1.2)';
            case 'hdr':
                return 'contrast(1.4) brightness(1.1) saturate(1.8)';
            case 'matte':
                return 'contrast(0.9) brightness(1.1) saturate(0.8)';
            case 'summer':
                return 'brightness(1.2) contrast(0.85) saturate(1.4)';
            case 'winter':
                return 'brightness(0.9) contrast(1.1) saturate(0.8) hue-rotate(180deg)';
            default:
                return 'none';
        }
    }

    // Reset preset selection
    reset() {
        this.presetItems.forEach(p => p.classList.remove('active'));
        this.selectedPreset = null;
        this.originalImageSrc = null;
        this.imagePreview.style.filter = 'none';
    }
}

// Initialize the presets tool when the window loads
window.addEventListener('load', () => {
    window.presetsTool = new PresetsTool();
});