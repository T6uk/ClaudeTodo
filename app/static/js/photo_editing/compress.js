// app/static/js/photo_editing/compress.js

/**
 * Image compression functionality for photo editing
 */
class CompressTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');

        // Compression controls
        this.qualitySlider = document.getElementById('quality-slider');
        this.qualityValue = document.getElementById('quality-value');
        this.sizeEstimate = document.getElementById('size-estimate');
        this.compressBtn = document.getElementById('compress-btn');

        // Original image size
        this.originalSize = 0;

        this.init();
    }

    init() {
        // Update quality display
        this.qualitySlider.addEventListener('input', () => {
            this.qualityValue.textContent = `${this.qualitySlider.value}%`;
            this.estimateFileSize();
        });

        // Initialize quality display
        this.qualityValue.textContent = `${this.qualitySlider.value}%`;

        // Compress button handler
        this.compressBtn.addEventListener('click', () => {
            this.compressImage();
        });

        // Listen for image loaded
        document.addEventListener('imageLoaded', (e) => {
            this.calculateOriginalSize(e.detail.image);
        });
    }

    // Calculate and display original image size
    calculateOriginalSize(imageData) {
        // Rough calculation based on base64 string
        if (typeof imageData === 'string' && imageData.startsWith('data:')) {
            const base64Length = imageData.length - (imageData.indexOf(',') + 1);
            const sizeInBytes = (base64Length * 3) / 4;
            this.originalSize = sizeInBytes;
            this.estimateFileSize();
        }
    }

    // Estimate file size based on quality setting
    estimateFileSize() {
        if (this.originalSize > 0) {
            const quality = parseInt(this.qualitySlider.value) / 100;
            // Rough estimation; actual compression depends on image content
            const estimatedSize = this.originalSize * quality * 0.7;

            let displaySize;
            if (estimatedSize > 1024 * 1024) {
                displaySize = `~${(estimatedSize / (1024 * 1024)).toFixed(2)} MB`;
            } else {
                displaySize = `~${(estimatedSize / 1024).toFixed(2)} KB`;
            }

            this.sizeEstimate.textContent = displaySize;
        }
    }

    // Compress the image
    compressImage() {
        // Create form data for the request
        const formData = new FormData();

        const quality = parseInt(this.qualitySlider.value);

        // Convert current image to blob and append to form
        PhotoUtils.urlToFile(window.currentImage || window.originalImage, "image.jpg", "image/jpeg")
            .then(imageFile => {
                formData.append('image', imageFile);
                formData.append('quality', quality);

                // Show loading state
                PhotoUtils.toggleButtonLoading(
                    this.compressBtn,
                    true,
                    '<i class="fas fa-compress me-2"></i> Compress Image',
                    '<i class="fas fa-spinner fa-spin me-2"></i> Processing...'
                );

                // Send the request to the server
                fetch('/utils/compress-image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show the result
                        window.showResult(data.image);

                        // Show size reduction
                        if (data.original_size && data.compressed_size) {
                            const reduction = (1 - (data.compressed_size / data.original_size)) * 100;
                            const message = `Size reduced by ${reduction.toFixed(1)}% (from ${this.formatSize(data.original_size)} to ${this.formatSize(data.compressed_size)})`;
                            alert(message);
                        }
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
                        this.compressBtn,
                        false,
                        '<i class="fas fa-compress me-2"></i> Compress Image',
                        ''
                    );
                });
            });
    }

    // Format size in human-readable format
    formatSize(sizeInBytes) {
        if (sizeInBytes > 1024 * 1024) {
            return `${(sizeInBytes / (1024 * 1024)).toFixed(2)} MB`;
        } else {
            return `${(sizeInBytes / 1024).toFixed(2)} KB`;
        }
    }

    // Reset compression controls
    reset() {
        this.qualitySlider.value = 80;
        this.qualityValue.textContent = '80%';
        this.sizeEstimate.textContent = '';
        this.originalSize = 0;
    }
}

// Initialize the compress tool when the window loads
window.addEventListener('load', () => {
    window.compressTool = new CompressTool();
});