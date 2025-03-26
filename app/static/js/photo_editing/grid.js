// app/static/js/photo_editing/grid.js

/**
 * Grid functionality for photo editing
 */
class GridTool {
    constructor() {
        this.imagePreview = document.getElementById('image-preview');
        this.originalImage = null;
        this.currentImage = null;

        // Grid controls
        this.gridType = document.getElementById('grid-type');
        this.customGridOptions = document.getElementById('custom-grid-options');
        this.gridColumns = document.getElementById('grid-columns');
        this.gridRows = document.getElementById('grid-rows');
        this.gridColor = document.getElementById('grid-color');
        this.gridOpacity = document.getElementById('grid-opacity');
        this.gridThickness = document.getElementById('grid-thickness');
        this.gridOpacityValue = document.getElementById('grid-opacity-value');
        this.gridThicknessValue = document.getElementById('grid-thickness-value');
        this.applyGridBtn = document.getElementById('apply-grid-btn');
        this.removeGridBtn = document.getElementById('remove-grid-btn');
        this.downloadGridBtn = document.getElementById('download-grid-btn');

        this.init();
    }

    init() {
        // Show/hide custom grid options based on selection
        this.gridType.addEventListener('change', () => {
            if (this.gridType.value === 'custom') {
                this.customGridOptions.style.display = 'block';
            } else {
                this.customGridOptions.style.display = 'none';
            }
        });

        // Update displayed values
        this.gridOpacity.addEventListener('input', () => {
            this.gridOpacityValue.textContent = this.gridOpacity.value;
        });

        this.gridThickness.addEventListener('input', () => {
            this.gridThicknessValue.textContent = this.gridThickness.value + 'px';
        });

        // Apply grid button handler
        this.applyGridBtn.addEventListener('click', () => {
            const type = this.gridType.value;
            const columns = parseInt(this.gridColumns.value) || 3;
            const rows = parseInt(this.gridRows.value) || 3;
            const color = this.gridColor.value;
            const opacity = parseFloat(this.gridOpacity.value);
            const thickness = parseInt(this.gridThickness.value);

            // Confirm with the user that this will modify the image
            if (confirm('This will apply the grid directly to the image. Continue?')) {
                this.applyGridOverlay(type, columns, rows, color, opacity, thickness);
            }
        });

        // Remove grid button handler
        this.removeGridBtn.addEventListener('click', () => {
            this.removeGridOverlay();
        });

        // Download grid button
        this.downloadGridBtn.addEventListener('click', () => {
            // Create a temporary link for downloading
            const link = document.createElement('a');
            link.href = window.currentImage || window.originalImage;
            link.download = 'image-with-grid.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

    setImages(original, current) {
        this.originalImage = original;
        this.currentImage = current;
    }

    // Apply grid overlay to the image
    applyGridOverlay(type, columns, rows, color, opacity, thickness) {
    // Remove any existing grid first
    this.removeGridOverlay();

    // Create a canvas element
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Load the current image
    const img = new Image();
    img.onload = () => {
        // Set canvas dimensions to match image
        canvas.width = img.width;
        canvas.height = img.height;

        // Draw the original image to the canvas
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Set up grid line style
        ctx.strokeStyle = PhotoUtils.hexToRgba(color, opacity);
        ctx.lineWidth = thickness;

        // Define grid lines based on grid type
        let horizontalLines = [];
        let verticalLines = [];

        if (type === 'rule-of-thirds') {
            // Rule of thirds - 2 horizontal and 2 vertical lines
            horizontalLines = [1/3, 2/3];
            verticalLines = [1/3, 2/3];
        } else if (type === 'golden-ratio') {
            // Golden ratio grid - phi ≈ 0.618
            const phi = 0.618;
            horizontalLines = [phi, 1 - phi];
            verticalLines = [phi, 1 - phi];

            // Add diagonal lines for golden spiral reference
            ctx.save();
            ctx.strokeStyle = PhotoUtils.hexToRgba(color, opacity * 0.7);
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(canvas.width, canvas.height);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(canvas.width, 0);
            ctx.lineTo(0, canvas.height);
            ctx.stroke();
            ctx.restore();
        } else if (type === 'custom') {
            // Custom grid with user-defined rows and columns
            for (let i = 1; i < rows; i++) {
                horizontalLines.push(i / rows);
            }

            for (let i = 1; i < columns; i++) {
                verticalLines.push(i / columns);
            }
        }

        // Draw horizontal grid lines
        horizontalLines.forEach(ratio => {
            const y = Math.round(ratio * canvas.height);
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        });

        // Draw vertical grid lines
        verticalLines.forEach(ratio => {
            const x = Math.round(ratio * canvas.width);
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        });

        // Convert canvas to data URL and display
        const gridImageData = canvas.toDataURL('image/png');

        // Update the preview image with the grid applied
        this.imagePreview.src = gridImageData;

        // Update current image with the grid applied
        window.currentImage = gridImageData;

        // Emit an event to notify other components
        const event = new CustomEvent('gridApplied', {
            detail: { image: gridImageData }
        });
        document.dispatchEvent(event);
    };

    // Set the image source to trigger loading
    img.src = window.currentImage || window.originalImage;
}

    // Remove grid overlay
    removeGridOverlay() {
        // Reset the image to its original state without the grid
        if (window.currentImage !== window.originalImage && window.originalImage) {
            this.imagePreview.src = window.originalImage;
            window.currentImage = window.originalImage;

            // Emit an event to notify other components
            const event = new CustomEvent('gridRemoved', {
                detail: { image: window.originalImage }
            });
            document.dispatchEvent(event);
        }
    }

    // Reset grid controls
    reset() {
        this.gridType.value = 'rule-of-thirds';
        this.customGridOptions.style.display = 'none';
        this.gridColumns.value = 3;
        this.gridRows.value = 3;
        this.gridColor.value = '#ffffff';
        this.gridOpacity.value = 0.7;
        this.gridOpacityValue.textContent = '0.7';
        this.gridThickness.value = 1;
        this.gridThicknessValue.textContent = '1px';
    }
}

// Initialize the grid tool when the window loads
window.addEventListener('load', () => {
    window.gridTool = new GridTool();
});