// app/static/js/photo_editing/inpaint.js

/**
 * Enhanced inpainting functionality for photo editing
 */
class InpaintTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');
        this.canvas = document.getElementById('inpaint-canvas');
        this.canvasContainer = document.getElementById('inpaint-canvas-container');
        this.ctx = this.canvas.getContext('2d');

        // Inpaint controls
        this.brushSizeSlider = document.getElementById('brush-size-slider');
        this.brushSizeValue = document.getElementById('brush-size-value');
        this.inpaintMethodSelect = document.getElementById('inpaint-method');
        this.inpaintRadiusSlider = document.getElementById('inpaint-radius-slider');
        this.inpaintRadiusValue = document.getElementById('inpaint-radius-value');
        this.clearMaskBtn = document.getElementById('clear-mask-btn');
        this.inpaintBtn = document.getElementById('inpaint-btn');
        this.undoBtn = document.getElementById('undo-mask-btn');

        // Drawing state
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;
        this.brushSize = 20;
        this.imageLoaded = false;
        this.drawHistory = [];
        this.maxHistorySteps = 20;

        this.init();
    }

    init() {
        // Update brush size display
        this.brushSizeSlider.addEventListener('input', () => {
            this.brushSize = parseInt(this.brushSizeSlider.value);
            this.brushSizeValue.textContent = `${this.brushSize}px`;
        });

        // Initialize brush size
        this.brushSize = parseInt(this.brushSizeSlider.value);
        this.brushSizeValue.textContent = `${this.brushSize}px`;

        // Update inpaint radius display
        this.inpaintRadiusSlider.addEventListener('input', () => {
            this.inpaintRadiusValue.textContent = `${this.inpaintRadiusSlider.value}px`;
        });

        // Initialize drawing events
        this.canvas.addEventListener('mousedown', (e) => {
            e.preventDefault(); // Prevent drag behavior
            this.startDrawing(e);
        });

        this.canvas.addEventListener('mousemove', (e) => {
            e.preventDefault(); // Prevent drag behavior
            this.draw(e);
        });

        this.canvas.addEventListener('mouseup', (e) => {
            e.preventDefault(); // Prevent drag behavior
            this.stopDrawing();
        });

        this.canvas.addEventListener('mouseleave', (e) => {
            e.preventDefault(); // Prevent drag behavior
            this.stopDrawing();
        });

        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            this.isDrawing = true;
            this.lastX = touch.clientX - rect.left;
            this.lastY = touch.clientY - rect.top;
            this.draw({ clientX: touch.clientX, clientY: touch.clientY });
        });

        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!this.isDrawing) return;
            const touch = e.touches[0];
            this.draw({ clientX: touch.clientX, clientY: touch.clientY });
        });

        this.canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopDrawing();
        });

        // Clear mask button
        this.clearMaskBtn.addEventListener('click', () => this.clearMask());

        // Undo button
        if (this.undoBtn) {
            this.undoBtn.addEventListener('click', () => this.undoLastDraw());
        }

        // Inpaint button
        this.inpaintBtn.addEventListener('click', () => this.applyInpainting());

        // Listen for tool activation
        document.addEventListener('toolActivated', (e) => {
            if (e.detail.tool === 'inpaint') {
                // Delay the canvas setup to ensure image is displayed
                setTimeout(() => this.setupCanvas(), 100);
            }
        });

        // Listen for image loaded
        document.addEventListener('imageLoaded', () => {
            this.imageLoaded = true;
            if (window.currentTool === 'inpaint') {
                setTimeout(() => this.setupCanvas(), 100);
            }
        });

        // Add key event for undo (Ctrl+Z)
        document.addEventListener('keydown', (e) => {
            if (window.currentTool === 'inpaint' && (e.ctrlKey || e.metaKey) && e.key === 'z') {
                e.preventDefault();
                this.undoLastDraw();
            }
        });
    }

    setupCanvas() {
        // First, check if the image is loaded and visible
        if (!this.imagePreview.complete || this.imagePreview.naturalWidth === 0) {
            console.log('Image not ready yet, waiting...');
            this.imagePreview.onload = () => this.setupCanvas();
            return;
        }

        // Get dimensions and position of the image preview
        const rect = this.imagePreview.getBoundingClientRect();

        // Set canvas dimensions
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;

        // Position canvas directly over the image
        this.canvasContainer.style.position = 'relative';
        this.canvasContainer.style.width = `${rect.width}px`;
        this.canvasContainer.style.height = `${rect.height}px`;

        // Display the image inside the canvas container as a background
        this.canvasContainer.style.backgroundImage = `url(${this.imagePreview.src})`;
        this.canvasContainer.style.backgroundSize = 'contain';
        this.canvasContainer.style.backgroundRepeat = 'no-repeat';
        this.canvasContainer.style.backgroundPosition = 'center';

        // Position canvas absolutely within container
        this.canvas.style.position = 'absolute';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';

        // Make the canvas visible
        this.canvas.style.display = 'block';

        // Clear any previous drawings
        this.clearMask();

        console.log('Canvas setup complete', this.canvas.width, this.canvas.height);
    }

    startDrawing(e) {
        // Save current canvas state for undo
        this.saveDrawState();

        const rect = this.canvas.getBoundingClientRect();
        this.isDrawing = true;
        this.lastX = e.clientX - rect.left;
        this.lastY = e.clientY - rect.top;

        // Immediately draw a dot at the starting position
        this.ctx.beginPath();
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        this.ctx.arc(this.lastX, this.lastY, this.brushSize / 2, 0, Math.PI * 2);
        this.ctx.fill();
    }

    draw(e) {
        if (!this.isDrawing) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Draw a line from last position to current position
        this.ctx.beginPath();
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
        this.ctx.lineWidth = this.brushSize;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.moveTo(this.lastX, this.lastY);
        this.ctx.lineTo(x, y);
        this.ctx.stroke();

        // Draw a circle at the current position
        this.ctx.beginPath();
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        this.ctx.arc(x, y, this.brushSize / 2, 0, Math.PI * 2);
        this.ctx.fill();

        this.lastX = x;
        this.lastY = y;
    }

    stopDrawing() {
        if (this.isDrawing) {
            this.isDrawing = false;
        }
    }

    saveDrawState() {
        // Save the current canvas state to history
        if (this.drawHistory.length >= this.maxHistorySteps) {
            this.drawHistory.shift(); // Remove oldest state if we reached max history
        }
        this.drawHistory.push(this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height));
    }

    undoLastDraw() {
        if (this.drawHistory.length > 0) {
            const prevState = this.drawHistory.pop();
            this.ctx.putImageData(prevState, 0, 0);
        } else {
            console.log('No more history to undo');
        }
    }

    clearMask() {
        if (this.ctx) {
            // Save current state before clearing
            this.saveDrawState();
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }

    applyInpainting() {
        if (!window.currentImage) {
            alert('Please load an image first');
            return;
        }

        // Convert the semi-transparent mask to solid white for the algorithm
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        tempCanvas.width = this.canvas.width;
        tempCanvas.height = this.canvas.height;

        // Draw the mask on the temp canvas
        tempCtx.drawImage(this.canvas, 0, 0);

        // Get the image data
        const imageData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
        const data = imageData.data;

        // Convert any non-transparent pixel to white (for the mask)
        for (let i = 0; i < data.length; i += 4) {
            if (data[i + 3] > 0) {  // If pixel has any opacity
                data[i] = 255;      // R
                data[i + 1] = 255;  // G
                data[i + 2] = 255;  // B
                data[i + 3] = 255;  // A (fully opaque)
            } else {
                data[i + 3] = 0;    // Fully transparent
            }
        }

        // Put the modified data back
        tempCtx.putImageData(imageData, 0, 0);

        // Get the mask as a data URL
        const maskDataUrl = tempCanvas.toDataURL('image/png');

        // Create form data for the request
        const formData = new FormData();

        // Convert current image to blob and append to form
        PhotoUtils.urlToFile(window.currentImage || window.originalImage, "image.jpg", "image/jpeg")
            .then(imageFile => {
                formData.append('image', imageFile);
                formData.append('mask', maskDataUrl);
                formData.append('method', this.inpaintMethodSelect.value);
                formData.append('radius', this.inpaintRadiusSlider.value);

                // Show loading state
                PhotoUtils.toggleButtonLoading(
                    this.inpaintBtn,
                    true,
                    '<i class="fas fa-magic me-2"></i> Apply Inpainting',
                    '<i class="fas fa-spinner fa-spin me-2"></i> Processing...'
                );

                // Send the request to the server
                fetch('/utils/inpaint-image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show the result
                        window.showResult(data.image);

                        // Clear the mask
                        this.clearMask();
                        // Clear history after successful inpainting
                        this.drawHistory = [];
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
                        this.inpaintBtn,
                        false,
                        '<i class="fas fa-magic me-2"></i> Apply Inpainting',
                        ''
                    );
                });
            });
    }

    // Reset inpainting controls
    reset() {
        this.clearMask();
        this.drawHistory = [];
        this.brushSizeSlider.value = 20;
        this.brushSize = 20;
        this.brushSizeValue.textContent = '20px';
        this.inpaintMethodSelect.value = '1';
        this.inpaintRadiusSlider.value = '10';
        this.inpaintRadiusValue.textContent = '10px';
    }
}

// Initialize the inpaint tool when the window loads
window.addEventListener('load', () => {
    window.inpaintTool = new InpaintTool();
});