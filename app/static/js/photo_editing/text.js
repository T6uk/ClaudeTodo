// app/static/js/photo_editing/text.js

/**
 * Text overlay functionality for photo editing
 */
class TextTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');
        this.canvas = document.getElementById('text-canvas');
        this.canvasContainer = document.getElementById('text-canvas-container');
        this.ctx = this.canvas.getContext('2d');

        // Text controls
        this.textInput = document.getElementById('text-input');
        this.textFont = document.getElementById('text-font');
        this.textSize = document.getElementById('text-size');
        this.textColor = document.getElementById('text-color');
        this.textAlign = document.getElementById('text-align');
        this.textBold = document.getElementById('text-bold');
        this.textItalic = document.getElementById('text-italic');
        this.textShadow = document.getElementById('text-shadow');
        this.textShadowColor = document.getElementById('text-shadow-color');
        this.addTextBtn = document.getElementById('add-text-btn');
        this.clearTextBtn = document.getElementById('clear-text-btn');
        this.applyTextBtn = document.getElementById('apply-text-btn');

        // Text objects array
        this.textItems = [];
        this.selectedTextIndex = -1;
        this.draggedTextIndex = -1;
        this.dragStartX = 0;
        this.dragStartY = 0;

        this.init();
    }

    init() {
        // Initialize canvas events
        this.canvas.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.handleMouseDown(e);
        });

        this.canvas.addEventListener('mousemove', (e) => {
            e.preventDefault();
            this.handleMouseMove(e);
        });

        this.canvas.addEventListener('mouseup', (e) => {
            e.preventDefault();
            this.handleMouseUp(e);
        });

        // Add text button
        this.addTextBtn.addEventListener('click', () => {
            this.addText();
        });

        // Clear text button
        this.clearTextBtn.addEventListener('click', () => {
            this.clearText();
        });

        // Apply text button
        this.applyTextBtn.addEventListener('click', () => {
            this.applyText();
        });

        // Update preview when text properties change
        this.textInput.addEventListener('input', () => this.updateSelectedText());
        this.textFont.addEventListener('change', () => this.updateSelectedText());
        this.textSize.addEventListener('change', () => this.updateSelectedText());
        this.textColor.addEventListener('change', () => this.updateSelectedText());
        this.textAlign.addEventListener('change', () => this.updateSelectedText());
        this.textBold.addEventListener('change', () => this.updateSelectedText());
        this.textItalic.addEventListener('change', () => this.updateSelectedText());
        this.textShadow.addEventListener('change', () => this.updateSelectedText());
        this.textShadowColor.addEventListener('change', () => this.updateSelectedText());

        // Listen for tool activation
        document.addEventListener('toolActivated', (e) => {
            if (e.detail.tool === 'text') {
                setTimeout(() => this.setupCanvas(), 100);
            }
        });

        // Listen for when the image is loaded
        document.addEventListener('imageLoaded', () => {
            if (window.currentTool === 'text') {
                setTimeout(() => this.setupCanvas(), 100);
            }
        });
        document.getElementById('text-shadow').addEventListener('change', function () {
            const shadowColorContainer = document.getElementById('shadow-color-container');
            if (this.checked) {
                shadowColorContainer.style.display = 'block';
            } else {
                shadowColorContainer.style.display = 'none';
            }
        });

        // Initialize shadow color visibility
        if (!document.getElementById('text-shadow').checked) {
            document.getElementById('shadow-color-container').style.display = 'none';
        }
    }

    setupCanvas() {
        // First, check if the image is loaded and visible
        if (!this.imagePreview || !this.imagePreview.complete || this.imagePreview.naturalWidth === 0) {
            console.log('Image not ready yet, waiting...');
            if (this.imagePreview) {
                this.imagePreview.onload = () => this.setupCanvas();
            }
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

        // Draw any existing text items
        this.redrawCanvas();

        console.log('Text canvas setup complete', this.canvas.width, this.canvas.height);
    }

    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Check if clicking on a text item
        for (let i = this.textItems.length - 1; i >= 0; i--) {
            const text = this.textItems[i];

            // Calculate text width
            this.ctx.font = this.getTextFont(text);
            const textWidth = this.ctx.measureText(text.text).width;
            const textHeight = parseInt(text.size);

            // Check if click is inside text bounding box
            if (x >= text.x && x <= text.x + textWidth &&
                y >= text.y - textHeight && y <= text.y) {

                this.draggedTextIndex = i;
                this.selectedTextIndex = i;
                this.dragStartX = x - text.x;
                this.dragStartY = y - text.y;

                // Update form controls with selected text properties
                this.textInput.value = text.text;
                this.textFont.value = text.font;
                this.textSize.value = text.size;
                this.textColor.value = text.color;
                this.textAlign.value = text.align;
                this.textBold.checked = text.bold;
                this.textItalic.checked = text.italic;
                this.textShadow.checked = text.shadow;
                this.textShadowColor.value = text.shadowColor;

                this.redrawCanvas();
                return;
            }
        }

        // If not clicking on text, deselect
        this.selectedTextIndex = -1;
        this.redrawCanvas();
    }

    handleMouseMove(e) {
        if (this.draggedTextIndex === -1) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Update text position
        this.textItems[this.draggedTextIndex].x = x - this.dragStartX;
        this.textItems[this.draggedTextIndex].y = y - this.dragStartY;

        this.redrawCanvas();
    }

    // app/static/js/photo_editing/text.js (continued)
    handleMouseUp(e) {
        this.draggedTextIndex = -1;
    }

    addText() {
        const text = this.textInput.value.trim();
        if (!text) {
            alert('Please enter some text');
            return;
        }

        // Create new text object
        const newText = {
            text: text,
            x: this.canvas.width / 2,
            y: this.canvas.height / 2,
            font: this.textFont.value,
            size: this.textSize.value,
            color: this.textColor.value,
            align: this.textAlign.value,
            bold: this.textBold.checked,
            italic: this.textItalic.checked,
            shadow: this.textShadow.checked,
            shadowColor: this.textShadowColor.value
        };

        // Add to text items array
        this.textItems.push(newText);

        // Select the new text
        this.selectedTextIndex = this.textItems.length - 1;

        // Redraw canvas
        this.redrawCanvas();
    }

    updateSelectedText() {
        if (this.selectedTextIndex === -1) return;

        // Update selected text with current control values
        this.textItems[this.selectedTextIndex] = {
            ...this.textItems[this.selectedTextIndex],
            text: this.textInput.value,
            font: this.textFont.value,
            size: this.textSize.value,
            color: this.textColor.value,
            align: this.textAlign.value,
            bold: this.textBold.checked,
            italic: this.textItalic.checked,
            shadow: this.textShadow.checked,
            shadowColor: this.textShadowColor.value
        };

        // Redraw canvas
        this.redrawCanvas();
    }

    getTextFont(textItem) {
        let font = '';

        // Add italic and bold if needed
        if (textItem.bold) font += 'bold ';
        if (textItem.italic) font += 'italic ';

        // Add size and font family
        font += `${textItem.size}px ${textItem.font}`;

        return font;
    }

    redrawCanvas() {
        // Clear the canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw all text items
        this.textItems.forEach((text, index) => {
            // Set text properties
            this.ctx.font = this.getTextFont(text);
            this.ctx.fillStyle = text.color;
            this.ctx.textAlign = text.align;

            // Calculate position based on alignment
            let x = text.x;
            if (text.align === 'center') {
                x = text.x;
            } else if (text.align === 'right') {
                x = text.x + this.ctx.measureText(text.text).width;
            }

            // Add shadow if enabled
            if (text.shadow) {
                this.ctx.shadowOffsetX = 2;
                this.ctx.shadowOffsetY = 2;
                this.ctx.shadowBlur = 4;
                this.ctx.shadowColor = text.shadowColor;
            } else {
                this.ctx.shadowOffsetX = 0;
                this.ctx.shadowOffsetY = 0;
                this.ctx.shadowBlur = 0;
                this.ctx.shadowColor = 'transparent';
            }

            // Draw text
            this.ctx.fillText(text.text, x, text.y);

            // Draw selection indicator if this text is selected
            if (index === this.selectedTextIndex) {
                this.ctx.strokeStyle = '#00a8ff';
                this.ctx.lineWidth = 2;

                // Calculate text width and height
                const textWidth = this.ctx.measureText(text.text).width;
                const textHeight = parseInt(text.size);

                // Calculate bounding box coordinates based on alignment
                let boxX = text.x;
                if (text.align === 'center') {
                    boxX = text.x - textWidth / 2;
                } else if (text.align === 'right') {
                    boxX = text.x - textWidth;
                }

                // Draw bounding box
                this.ctx.strokeRect(
                    boxX - 5,
                    text.y - textHeight - 5,
                    textWidth + 10,
                    textHeight + 10
                );
            }
        });
    }

    clearText() {
        if (this.selectedTextIndex !== -1) {
            // Remove selected text
            this.textItems.splice(this.selectedTextIndex, 1);
            this.selectedTextIndex = -1;
        } else {
            // No text selected, clear all
            if (this.textItems.length > 0) {
                if (confirm('Remove all text?')) {
                    this.textItems = [];
                }
            }
        }

        // Redraw canvas
        this.redrawCanvas();
    }

    applyText() {
        if (this.textItems.length === 0) {
            alert('No text added. Please add text first.');
            return;
        }

        // Create a combined canvas with the image and text
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

            // Draw all text items to the temp canvas with scaling
            this.textItems.forEach(text => {
                // Set text properties with scaling
                const scaledSize = parseInt(text.size) * scaleX;
                const fontStyle = text.bold ? 'bold ' : '';
                const fontStyle2 = text.italic ? 'italic ' : '';
                tempCtx.font = `${fontStyle}${fontStyle2}${scaledSize}px ${text.font}`;
                tempCtx.fillStyle = text.color;
                tempCtx.textAlign = text.align;

                // Calculate position with scaling
                let x = text.x * scaleX;
                if (text.align === 'center') {
                    x = text.x * scaleX;
                } else if (text.align === 'right') {
                    x = text.x * scaleX + tempCtx.measureText(text.text).width;
                }

                // Add shadow if enabled
                if (text.shadow) {
                    tempCtx.shadowOffsetX = 2 * scaleX;
                    tempCtx.shadowOffsetY = 2 * scaleY;
                    tempCtx.shadowBlur = 4 * scaleX;
                    tempCtx.shadowColor = text.shadowColor;
                } else {
                    tempCtx.shadowOffsetX = 0;
                    tempCtx.shadowOffsetY = 0;
                    tempCtx.shadowBlur = 0;
                    tempCtx.shadowColor = 'transparent';
                }

                // Draw text
                tempCtx.fillText(text.text, x, text.y * scaleY);
            });

            // Get the combined image
            const dataURL = tempCanvas.toDataURL('image/png');

            // Show the result
            window.showResult(dataURL);

            // Clear the text canvas
            this.textItems = [];
            this.selectedTextIndex = -1;
            this.redrawCanvas();
        };

        img.src = window.currentImage || window.originalImage;
    }

    reset() {
        this.textItems = [];
        this.selectedTextIndex = -1;
        this.draggedTextIndex = -1;
        this.textInput.value = '';
        this.textFont.value = 'Arial';
        this.textSize.value = '24';
        this.textColor.value = '#ffffff';
        this.textAlign.value = 'left';
        this.textBold.checked = false;
        this.textItalic.checked = false;
        this.textShadow.checked = false;
        this.textShadowColor.value = '#000000';
        this.redrawCanvas();
    }
}

// Initialize the text tool when the window loads
window.addEventListener('load', () => {
    window.textTool = new TextTool();
});