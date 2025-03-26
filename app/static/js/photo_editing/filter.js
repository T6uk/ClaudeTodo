// app/static/js/photo_editing/filter.js

/**
 * Filter functionality for photo editing
 */
class FilterTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');

        // Filter controls
        this.filterPreviews = document.querySelectorAll('.filter-preview');
        this.filterBtn = document.getElementById('filter-btn');
        this.currentFilter = 'none';

        this.init();
    }

    init() {
        // Filter preview click
        this.filterPreviews.forEach(preview => {
            preview.addEventListener('click', () => {
                this.filterPreviews.forEach(p => p.classList.remove('active'));
                preview.classList.add('active');
                this.currentFilter = preview.getAttribute('data-filter');
            });
        });

        // Apply filter button
        this.filterBtn.addEventListener('click', () => {
            if (this.currentFilter === 'none') {
                // Reset to original image
                window.showResult(window.originalImage);
                return;
            }

            this.applyFilter(this.currentFilter);
        });

        // Initialize filter previews with sample images
        document.addEventListener('filterPreviewsReady', () => {
            this.generateFilterPreviews();
        });
    }

    // Generate filter previews
    generateFilterPreviews() {
        // Skip if there's no image yet
        if (!window.originalImage) return;

        this.filterPreviews.forEach(preview => {
            const filter = preview.getAttribute('data-filter');

            if (filter === 'none') {
                preview.src = window.originalImage;
                return;
            }

            // Create a small version for the preview
            const img = new Image();
            img.onload = () => {
                // Create a canvas for the preview
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');

                // Set small dimensions for the preview
                canvas.width = 120;
                canvas.height = 90;

                // Draw the image scaled down
                ctx.drawImage(img, 0, 0, img.width, img.height, 0, 0, canvas.width, canvas.height);

                // Apply a simple CSS filter for preview
                preview.style.filter = this.getCssFilter(filter);
                preview.src = window.originalImage;
            };

            img.src = window.originalImage;
        });
    }

    // Get CSS filter for preview
    getCssFilter(filter) {
        switch(filter) {
            case 'grayscale': return 'grayscale(100%)';
            case 'sepia': return 'sepia(100%)';
            case 'blur': return 'blur(2px)';
            case 'sharpen': return 'contrast(150%)';
            case 'emboss': return 'contrast(150%) brightness(80%)';
            case 'edge_enhance': return 'contrast(200%) brightness(120%)';
            case 'contour': return 'contrast(300%) brightness(80%)';
            case 'smooth': return 'blur(1px) brightness(105%)';
            case 'invert': return 'invert(100%)';
            default: return 'none';
        }
    }

    // Apply the selected filter
    applyFilter(filter) {
        // Create form data for the request
        const formData = new FormData();

        // Convert current image to blob and append to form
        PhotoUtils.urlToFile(window.currentImage || window.originalImage, "image.jpg", "image/jpeg")
            .then(imageFile => {
                formData.append('image', imageFile);
                formData.append('filter_type', filter);

                // Show loading state
                PhotoUtils.toggleButtonLoading(
                    this.filterBtn,
                    true,
                    '<i class="fas fa-adjust me-2"></i> Apply Filter',
                    '<i class="fas fa-spinner fa-spin me-2"></i> Processing...'
                );

                // Send the request to the server
                fetch('/utils/apply-filter', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
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
                        this.filterBtn,
                        false,
                        '<i class="fas fa-adjust me-2"></i> Apply Filter',
                        ''
                    );
                });
            });
    }

    // Reset filter selection
    reset() {
        this.filterPreviews.forEach(preview => {
            if (preview.getAttribute('data-filter') === 'none') {
                preview.classList.add('active');
            } else {
                preview.classList.remove('active');
            }
        });

        this.currentFilter = 'none';
    }
}

// Initialize the filter tool when the window loads
window.addEventListener('load', () => {
    window.filterTool = new FilterTool();

    // Trigger filter previews generation when an image is loaded
    document.addEventListener('imageLoaded', () => {
        window.filterTool.generateFilterPreviews();
    });
});