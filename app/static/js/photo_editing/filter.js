// app/static/js/photo_editing/filter.js

/**
 * Enhanced filter functionality for photo editing with live preview
 */
class FilterTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');

        // Filter controls
        this.filterPreviews = document.querySelectorAll('.filter-preview');
        this.filterBtn = document.getElementById('filter-btn');
        this.currentFilter = 'none';

        // Keep track of original image
        this.originalImageSrc = null;

        // Store current filter preview
        this.previewFilter = null;

        this.init();
    }

    init() {
        // Filter preview click
        this.filterPreviews.forEach(preview => {
            preview.addEventListener('click', () => {
                this.filterPreviews.forEach(p => p.classList.remove('active'));
                preview.classList.add('active');
                this.currentFilter = preview.getAttribute('data-filter');

                // Apply live preview when filter is selected
                this.applyFilterPreview(this.currentFilter);
            });

            // Add mouseover preview
            preview.addEventListener('mouseenter', () => {
                // Save current filter to restore on mouseleave
                if (!this.previewFilter) {
                    this.previewFilter = this.currentFilter;
                }

                // Show a temporary preview of this filter
                const filter = preview.getAttribute('data-filter');
                this.applyFilterPreview(filter, true);
            });

            // Reset to selected filter on mouseleave
            preview.addEventListener('mouseleave', () => {
                if (this.previewFilter) {
                    this.applyFilterPreview(this.previewFilter, true);
                    this.previewFilter = null;
                }
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

        // Listen for tool activation
        document.addEventListener('toolActivated', (e) => {
            if (e.detail.tool === 'filter') {
                this.initializeFilters();
            }
        });

        // Listen for image loaded
        document.addEventListener('imageLoaded', () => {
            this.generateFilterPreviews();
            if (window.currentTool === 'filter') {
                this.initializeFilters();
            }
        });

        const resetFilterBtn = document.getElementById('reset-filter-btn');
            if (resetFilterBtn) {
                resetFilterBtn.addEventListener('click', () => {
                    this.resetFilter();
                });
            }
    }

    // Initialize the filter tool
    initializeFilters() {
        // Store the original image state when the tool is activated
        this.originalImageSrc = window.currentImage || window.originalImage;

        // Reset any existing preview
        this.imagePreview.style.filter = 'none';

        // Generate filter previews
        this.generateFilterPreviews();
    }

    // Apply CSS filter preview
    applyFilterPreview(filter, isTemporary = false) {
        // Don't change the image for previews if we're just hovering
        if (filter === 'none') {
            this.imagePreview.style.filter = 'none';
            return;
        }

        // Apply CSS filter for immediate preview
        const cssFilter = this.getCssFilter(filter);
        this.imagePreview.style.filter = cssFilter;

        // If this is a selected filter (not just a hover), update the current filter
        if (!isTemporary) {
            this.currentFilter = filter;
        }
    }

    // Generate filter previews
    generateFilterPreviews() {
        // Skip if there's no image yet
        if (!window.originalImage) return;

        this.filterPreviews.forEach(preview => {
            const filter = preview.getAttribute('data-filter');

            if (filter === 'none') {
                preview.src = window.originalImage;
                preview.style.filter = 'none';
                return;
            }

            // Use the same source image for all previews, but apply CSS filter
            preview.src = window.originalImage;
            preview.style.filter = this.getCssFilter(filter);
        });
    }

    // Get CSS filter string for preview
    getCssFilter(filter) {
        switch(filter) {
            case 'grayscale': return 'grayscale(100%)';
            case 'sepia': return 'sepia(100%)';
            case 'blur': return 'blur(2px)';
            case 'sharpen': return 'contrast(150%) brightness(110%)';
            case 'emboss': return 'contrast(150%) brightness(80%)';
            case 'edge_enhance': return 'contrast(200%) brightness(120%)';
            case 'contour': return 'contrast(300%) brightness(80%)';
            case 'smooth': return 'blur(1px) brightness(105%)';
            case 'invert': return 'invert(100%)';
            default: return 'none';
        }
    }

    // Apply the selected filter (server-side)
    applyFilter(filter) {
        // Create form data for the request
        const formData = new FormData();

        // Convert original image to blob and append to form
        // We use the original image to avoid cumulative filter effects
        PhotoUtils.urlToFile(this.originalImageSrc || window.originalImage, "image.jpg", "image/jpeg")
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
        this.originalImageSrc = null;
        this.previewFilter = null;

        // Clear any filter styles
        this.imagePreview.style.filter = 'none';
    }

    // Then add this method to the class
    resetFilter() {
        // Reset to none filter
        this.filterPreviews.forEach(preview => {
            if (preview.getAttribute('data-filter') === 'none') {
                preview.classList.add('active');
            } else {
                preview.classList.remove('active');
            }
        });

        this.currentFilter = 'none';
        this.imagePreview.style.filter = 'none';

        // If we have a valid original image, show it
        if (this.originalImageSrc) {
            this.imagePreview.src = this.originalImageSrc;
        }
    }
}

// Initialize the filter tool when the window loads
window.addEventListener('load', () => {
    window.filterTool = new FilterTool();
});