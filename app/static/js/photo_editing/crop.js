// app/static/js/photo_editing/crop.js

/**
 * Crop functionality for photo editing
 */
class CropTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');

        // Crop controls
        this.cropBtn = document.getElementById('crop-btn');
        this.cropOverlay = document.getElementById('crop-overlay');
        this.cropContainer = document.getElementById('cropper-container');
        this.cropPreview = document.getElementById('crop-preview');

        // Crop handles
        this.handleNW = document.getElementById('handle-nw');
        this.handleNE = document.getElementById('handle-ne');
        this.handleSW = document.getElementById('handle-sw');
        this.handleSE = document.getElementById('handle-se');

        // Crop state
        this.isDragging = false;
        this.isResizing = false;
        this.currentHandle = null;
        this.startX = 0;
        this.startY = 0;
        this.startLeft = 0;
        this.startTop = 0;
        this.startWidth = 0;
        this.startHeight = 0;

        this.init();
    }

    init() {
        // Make crop overlay draggable
        this.cropOverlay.addEventListener('mousedown', (e) => {
            if (e.target === this.cropOverlay) {
                this.isDragging = true;
                this.startX = e.clientX;
                this.startY = e.clientY;
                this.startLeft = this.cropOverlay.offsetLeft;
                this.startTop = this.cropOverlay.offsetTop;
                e.preventDefault();
            }
        });

        // Make handles resizable
        [this.handleNW, this.handleNE, this.handleSW, this.handleSE].forEach(handle => {
            handle.addEventListener('mousedown', (e) => {
                this.isResizing = true;
                this.currentHandle = handle.id;
                this.startX = e.clientX;
                this.startY = e.clientY;
                this.startLeft = this.cropOverlay.offsetLeft;
                this.startTop = this.cropOverlay.offsetTop;
                this.startWidth = this.cropOverlay.offsetWidth;
                this.startHeight = this.cropOverlay.offsetHeight;
                e.preventDefault();
                e.stopPropagation();
            });
        });

        // Handle mouse move for both dragging and resizing
        document.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                const dx = e.clientX - this.startX;
                const dy = e.clientY - this.startY;

                let newLeft = this.startLeft + dx;
                let newTop = this.startTop + dy;

                // Constrain to container
                newLeft = Math.max(0, Math.min(newLeft, this.cropContainer.offsetWidth - this.cropOverlay.offsetWidth));
                newTop = Math.max(0, Math.min(newTop, this.cropContainer.offsetHeight - this.cropOverlay.offsetHeight));

                this.cropOverlay.style.left = newLeft + 'px';
                this.cropOverlay.style.top = newTop + 'px';
            } else if (this.isResizing) {
                const dx = e.clientX - this.startX;
                const dy = e.clientY - this.startY;

                let newLeft = this.startLeft;
                let newTop = this.startTop;
                let newWidth = this.startWidth;
                let newHeight = this.startHeight;

                switch (this.currentHandle) {
                    case 'handle-nw':
                        newLeft = this.startLeft + dx;
                        newTop = this.startTop + dy;
                        newWidth = this.startWidth - dx;
                        newHeight = this.startHeight - dy;
                        break;
                    case 'handle-ne':
                        newTop = this.startTop + dy;
                        newWidth = this.startWidth + dx;
                        newHeight = this.startHeight - dy;
                        break;
                    case 'handle-sw':
                        newLeft = this.startLeft + dx;
                        newWidth = this.startWidth - dx;
                        newHeight = this.startHeight + dy;
                        break;
                    case 'handle-se':
                        newWidth = this.startWidth + dx;
                        newHeight = this.startHeight + dy;
                        break;
                }

                // Ensure minimum size and constrain to container
                if (newWidth >= 20 && newHeight >= 20) {
                    if (newLeft >= 0 && newLeft + newWidth <= this.cropContainer.offsetWidth) {
                        this.cropOverlay.style.left = newLeft + 'px';
                        this.cropOverlay.style.width = newWidth + 'px';
                    }

                    if (newTop >= 0 && newTop + newHeight <= this.cropContainer.offsetHeight) {
                        this.cropOverlay.style.top = newTop + 'px';
                        this.cropOverlay.style.height = newHeight + 'px';
                    }
                }
            }
        });

        // Handle mouse up to stop dragging/resizing
        document.addEventListener('mouseup', () => {
            this.isDragging = false;
            this.isResizing = false;
            this.currentHandle = null;
        });

        // Crop button handler
        this.cropBtn.addEventListener('click', () => {
            const containerRect = this.cropContainer.getBoundingClientRect();
            const overlayRect = this.cropOverlay.getBoundingClientRect();

            // Calculate crop coordinates as ratios of the image size
            const left = (overlayRect.left - containerRect.left) / containerRect.width;
            const top = (overlayRect.top - containerRect.top) / containerRect.height;
            const right = left + (overlayRect.width / containerRect.width);
            const bottom = top + (overlayRect.height / containerRect.height);

            this.cropImage(left, top, right, bottom);
        });
    }

    // Initialize crop preview
    initCropPreview() {
        this.cropPreview.src = window.currentImage || window.originalImage;

        // Reset crop overlay to center 50% of image
        this.cropOverlay.style.top = '25%';
        this.cropOverlay.style.left = '25%';
        this.cropOverlay.style.width = '50%';
        this.cropOverlay.style.height = '50%';
    }

    // Crop the image to the specified coordinates
    cropImage(left, top, right, bottom) {
        // Create form data for the request
        const formData = new FormData();

        // Convert current image to blob and append to form
        PhotoUtils.urlToFile(window.currentImage || window.originalImage, "image.jpg", "image/jpeg")
            .then(imageFile => {
                formData.append('image', imageFile);
                formData.append('left', left);
                formData.append('top', top);
                formData.append('right', right);
                formData.append('bottom', bottom);

                // Show loading state
                PhotoUtils.toggleButtonLoading(
                    this.cropBtn,
                    true,
                    '<i class="fas fa-crop-alt me-2"></i> Apply Crop',
                    '<i class="fas fa-spinner fa-spin me-2"></i> Processing...'
                );

                // Send the request to the server
                fetch('/utils/crop-image', {
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
                        this.cropBtn,
                        false,
                        '<i class="fas fa-crop-alt me-2"></i> Apply Crop',
                        ''
                    );
                });
            });
    }

    // Reset crop overlay
    reset() {
        this.cropOverlay.style.top = '25%';
        this.cropOverlay.style.left = '25%';
        this.cropOverlay.style.width = '50%';
        this.cropOverlay.style.height = '50%';
    }
}

// Initialize the crop tool when the window loads
window.addEventListener('load', () => {
    window.cropTool = new CropTool();
});