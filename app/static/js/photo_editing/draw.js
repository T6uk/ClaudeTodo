// app/static/js/photo_editing/draw.js

/**
 * Drawing functionality for photo editing
 */
class DrawTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');
        this.canvas = document.getElementById('draw-canvas');
        this.canvasContainer = document.getElementById('draw-canvas-container');
        this.ctx = this.canvas.getContext('2d');

        // Drawing controls
        this.shapeType = document.getElementById('shape-type');
        this.strokeWidth = document.getElementById('stroke-width');
        this.strokeColor = document.getElementById('stroke-color');
        this.fillColor = document.getElementById('fill-color');
        this.clearDrawingBtn = document.getElementById('clear-drawing-btn');
        this.applyDrawingBtn = document.getElementById('apply-drawing-btn');
        this.undoDrawingBtn = document.getElementById('undo-drawing-btn');

        // Drawing state
        this.isDrawing = false;
        this.startX = 0;
        this.startY = 0;
        this.shapes = [];
        this.currentShape = null;
        this.drawHistory = [];

        this.init();
    }

    init() {
        // Initialize canvas events
        this.canvas.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.startDrawing(e);
        });

        this.canvas.addEventListener('mousemove', (e) => {
            e.preventDefault();
            this.draw(e);
        });

        this.canvas.addEventListener('mouseup', (e) => {
            e.preventDefault();
            this.stopDrawing();
        });

        this.canvas.addEventListener('mouseleave', (e) => {
            e.preventDefault();
            this.stopDrawing();
        });

        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            this.startX = touch.clientX - rect.left;
            this.startY = touch.clientY - rect.top;
            this.isDrawing = true;

            // Create a new shape
            this.currentShape = {
                type: this.shapeType.value,
                startX: this.startX,
                startY: this.startY,
                endX: this.startX,
                endY: this.startY,
                strokeWidth: parseInt(this.strokeWidth.value),
                strokeColor: this.strokeColor.value,
                fillColor: this.fillColor.value
            };

            this.redrawCanvas();
        });

        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!this.isDrawing) return;

            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            const x = touch.clientX - rect.left;
            const y = touch.clientY - rect.top;

            if (this.currentShape) {
                this.currentShape.endX = x;
                this.currentShape.endY = y;
                this.redrawCanvas();
            }
        });

        this.canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            if (this.isDrawing) {
                this.isDrawing = false;
                if (this.currentShape) {
                    this.shapes.push(this.currentShape);
                    this.currentShape = null;
                    this.saveDrawState();
                }
            }
        });

        // Clear drawing button
        this.clearDrawingBtn.addEventListener('click', () => {
            this.clearDrawing();
        });

        // Apply drawing button
        this.applyDrawingBtn.addEventListener('click', () => {
            this.applyDrawing();
        });

        // Undo button
        this.undoDrawingBtn.addEventListener('click', () => {
            this.undoLastShape();
        });

        // Listen for tool activation
        document.addEventListener('toolActivated', (e) => {
            if (e.detail.tool === 'draw') {
                setTimeout(() => this.setupCanvas(), 100);
            }
        });

        // Listen for when the image is loaded
        document.addEventListener('imageLoaded', () => {
            if (window.currentTool === 'draw') {
                setTimeout(() => this.setupCanvas(), 100);
            }
        });

        // Add to the init method
        this.transparentFill = document.getElementById('transparent-fill');

// When transparent-fill changes, update the fill color input disabled state
        this.transparentFill.addEventListener('change', () => {
            if (this.transparentFill.checked) {
                this.fillColor.disabled = true;
            } else {
                this.fillColor.disabled = false;
            }
        });

// Initialize disabled state
        if (this.transparentFill && this.transparentFill.checked) {
            this.fillColor.disabled = true;
        }
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
        this.clearDrawing();

        console.log('Drawing canvas setup complete', this.canvas.width, this.canvas.height);
    }

    startDrawing(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.startX = e.clientX - rect.left;
        this.startY = e.clientY - rect.top;
        this.isDrawing = true;

        // Create a new shape
        this.currentShape = {
            type: this.shapeType.value,
            startX: this.startX,
            startY: this.startY,
            endX: this.startX,
            endY: this.startY,
            strokeWidth: parseInt(this.strokeWidth.value),
            strokeColor: this.strokeColor.value,
            fillColor: this.transparentFill && this.transparentFill.checked ? 'transparent' : this.fillColor.value
        };

        this.redrawCanvas();
    }

    draw(e) {
        if (!this.isDrawing) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (this.currentShape) {
            this.currentShape.endX = x;
            this.currentShape.endY = y;
            this.redrawCanvas();
        }
    }

    stopDrawing() {
        if (this.isDrawing) {
            this.isDrawing = false;
            if (this.currentShape) {
                this.shapes.push(this.currentShape);
                this.currentShape = null;
                this.saveDrawState();
            }
        }
    }

    saveDrawState() {
        // Save current shapes to history
        this.drawHistory.push([...this.shapes]);
        // Update undo button state
        this.undoDrawingBtn.disabled = this.drawHistory.length <= 0;
    }

    undoLastShape() {
        if (this.drawHistory.length > 0) {
            // Pop the current state (we don't need it)
            this.drawHistory.pop();

            if (this.drawHistory.length > 0) {
                // Get the previous state
                this.shapes = [...this.drawHistory[this.drawHistory.length - 1]];
            } else {
                // If no history left, clear all shapes
                this.shapes = [];
            }

            this.redrawCanvas();

            // Update undo button state
            this.undoDrawingBtn.disabled = this.drawHistory.length <= 0;
        }
    }

    redrawCanvas() {
        // Clear the canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw all saved shapes
        this.shapes.forEach(shape => {
            this.drawShape(shape);
        });

        // Draw the current shape
        if (this.currentShape) {
            this.drawShape(this.currentShape);
        }
    }

    drawShape(shape) {
        this.ctx.lineWidth = shape.strokeWidth;
        this.ctx.strokeStyle = shape.strokeColor;
        this.ctx.fillStyle = shape.fillColor;

        // Calculate shape dimensions
        const width = shape.endX - shape.startX;
        const height = shape.endY - shape.startY;

        switch (shape.type) {
            case 'rectangle':
                this.ctx.beginPath();
                this.ctx.rect(shape.startX, shape.startY, width, height);
                if (shape.fillColor !== 'transparent') {
                    this.ctx.fill();
                }
                this.ctx.stroke();
                break;
            case 'circle':
                const radius = Math.sqrt(width * width + height * height) / 2;
                this.ctx.beginPath();
                this.ctx.arc(shape.startX, shape.startY, radius, 0, Math.PI * 2);
                if (shape.fillColor !== 'transparent') {
                    this.ctx.fill();
                }
                this.ctx.stroke();
                break;
            case 'line':
                this.ctx.beginPath();
                this.ctx.moveTo(shape.startX, shape.startY);
                this.ctx.lineTo(shape.endX, shape.endY);
                this.ctx.stroke();
                break;
            case 'arrow':
                // Draw line
                this.ctx.beginPath();
                this.ctx.moveTo(shape.startX, shape.startY);
                this.ctx.lineTo(shape.endX, shape.endY);
                this.ctx.stroke();

                // Calculate arrow head
                const angle = Math.atan2(shape.endY - shape.startY, shape.endX - shape.startX);
                const headLength = 15; // Length of arrow head in pixels

                // Draw arrow head
                this.ctx.beginPath();
                this.ctx.moveTo(shape.endX, shape.endY);
                this.ctx.lineTo(
                    shape.endX - headLength * Math.cos(angle - Math.PI / 6),
                    shape.endY - headLength * Math.sin(angle - Math.PI / 6)
                );
                this.ctx.moveTo(shape.endX, shape.endY);
                this.ctx.lineTo(
                    shape.endX - headLength * Math.cos(angle + Math.PI / 6),
                    shape.endY - headLength * Math.sin(angle + Math.PI / 6)
                );
                this.ctx.stroke();
                break;
        }
    }

    clearDrawing() {
        this.shapes = [];
        this.currentShape = null;
        this.drawHistory = [];
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        // Update undo button state
        this.undoDrawingBtn.disabled = true;
    }

    applyDrawing() {
        if (this.shapes.length === 0) {
            alert('No shapes drawn. Please draw something first.');
            return;
        }

        // Create a combined canvas with the image and drawings
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');

        // Set canvas dimensions to match original image
        const img = new Image();
        img.onload = () => {
            tempCanvas.width = img.width;
            tempCanvas.height = img.height;

            // Draw the image
            tempCtx.drawImage(img, 0, 0, tempCanvas.width, tempCanvas.height);

            // Calculate scale factor between canvas and original image
            const scaleX = img.width / this.canvas.width;
            const scaleY = img.height / this.canvas.height;

            // Scale and draw all shapes to the temp canvas
            tempCtx.scale(scaleX, scaleY);

            this.shapes.forEach(shape => {
                const scaledShape = {
                    ...shape,
                    strokeWidth: shape.strokeWidth, // Keep stroke width proportional
                };
                this.drawShape.call({ctx: tempCtx}, scaledShape);
            });

            // Get the combined image
            const dataURL = tempCanvas.toDataURL('image/png');

            // Show the result
            window.showResult(dataURL);

            // Clear the drawing canvas
            this.clearDrawing();
        };

        img.src = window.currentImage || window.originalImage;
    }

    reset() {
        this.clearDrawing();
        this.shapeType.value = 'rectangle';
        this.strokeWidth.value = 3;
        this.strokeColor.value = '#ff0000';
        this.fillColor.value = 'transparent';
    }
}

// Initialize the draw tool when the window loads
window.addEventListener('load', () => {
    window.drawTool = new DrawTool();
});