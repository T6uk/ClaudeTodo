// app/static/js/photo_editing/main.js

/**
 * Main functionality for photo editing
 */
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements - Upload & Preview
    const dropZone = document.getElementById('drop-zone');
    const imageUpload = document.getElementById('image-upload');
    const browseBtn = document.getElementById('browse-btn');
    const imagePreview = document.getElementById('image-preview');
    const previewActions = document.getElementById('preview-actions');
    const changeImageBtn = document.getElementById('change-image-btn');
    const removeImageBtn = document.getElementById('remove-image-btn');
    const toolSelector = document.getElementById('tool-selector');

    // Tool Controls
    const scalingControls = document.getElementById('scaling-controls');
    const rotationControls = document.getElementById('rotation-controls');
    const cropControls = document.getElementById('crop-controls');
    const filterControls = document.getElementById('filter-controls');
    const adjustControls = document.getElementById('adjust-controls');
    const gridControls = document.getElementById('grid-controls');

    // Result Elements
    const imageResult = document.getElementById('image-result');
    const resultPreview = document.getElementById('result-preview');
    const editAgainBtn = document.getElementById('edit-again-btn');
    const applyMoreBtn = document.getElementById('apply-more-btn');
    const downloadBtn = document.getElementById('download-btn');

    // Global state (available to other modules)
    window.originalImage = null;
    window.currentImage = null;
    window.aspectRatio = 1;
    window.currentTool = 'scaling';

    // Initialize main app
    init();

    function init() {
        // File Upload via Browse Button
        browseBtn.addEventListener('click', function() {
            imageUpload.click();
        });

        // Handle file selection
        imageUpload.addEventListener('change', function(e) {
            handleFiles(e.target.files);
        });

        // Drag and Drop handlers
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('active');
        });

        dropZone.addEventListener('dragleave', function() {
            dropZone.classList.remove('active');
        });

        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('active');

            if (e.dataTransfer.files.length) {
                handleFiles(e.dataTransfer.files);
            }
        });

        // Change image button
        changeImageBtn.addEventListener('click', function() {
            imageUpload.click();
        });

        // Remove image button
        removeImageBtn.addEventListener('click', function() {
            resetImageEditor();
        });

        // Tool selector buttons
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const tool = this.getAttribute('data-tool');
                setActiveTool(tool);
            });
        });

        // Edit again button
        editAgainBtn.addEventListener('click', function() {
            imageResult.style.display = 'none';
            showToolControls();
        });

        // Apply more edits button
        applyMoreBtn.addEventListener('click', function() {
            // Update current image state
            window.currentImage = resultPreview.src;

            // Hide result view
            imageResult.style.display = 'none';

            // Update preview
            imagePreview.src = window.currentImage;

            // Show tool controls
            showToolControls();
        });

        // Download button
        downloadBtn.addEventListener('click', function() {
            this.href = window.currentImage;
        });

        // Export global functions used by other modules
        window.showResult = showResult;
        window.resetAllTools = resetAllTools;
        window.initializeFilterPreviews = initializeFilterPreviews;
    }

    // Functions to handle image upload and display
    function handleFiles(files) {
        if (files && files[0]) {
            const file = files[0];

            // Check if file is an image
            if (!file.type.match('image.*')) {
                alert('Please select an image file');
                return;
            }

            const reader = new FileReader();

            reader.onload = function(e) {
                // Store original image
                window.originalImage = e.target.result;
                window.currentImage = window.originalImage;

                // Display the image preview
                imagePreview.src = e.target.result;
                imagePreview.classList.remove('d-none');
                dropZone.style.display = 'none';
                previewActions.classList.remove('d-none');
                toolSelector.classList.remove('d-none');

                // Show scaling controls by default
                setActiveTool('scaling');

                // Create a new image to get dimensions
                const img = new Image();
                img.onload = function() {
                    window.aspectRatio = img.width / img.height;

                    // Set initial values for width and height inputs
                    document.getElementById('width-input').value = img.width;
                    document.getElementById('height-input').value = img.height;

                    // Initialize filter previews
                    initializeFilterPreviews(e.target.result);

                    // Initialize crop preview
                    document.getElementById('crop-preview').src = e.target.result;

                    // Notify tools of image update
                    if (window.gridTool) window.gridTool.setImages(window.originalImage, window.currentImage);
                };
                img.src = e.target.result;
            };

            reader.readAsDataURL(file);
        }
    }

    function resetImageEditor() {
        imagePreview.classList.add('d-none');
        imagePreview.src = '';
        dropZone.style.display = 'flex';
        previewActions.classList.add('d-none');
        toolSelector.classList.add('d-none');
        hideAllToolControls();
        imageResult.style.display = 'none';

        // Reset values
        window.originalImage = null;
        window.currentImage = null;
        imageUpload.value = '';

        // Reset tool states
        resetAllTools();
    }

    function setActiveTool(tool) {
        window.currentTool = tool;

        // Update button states
        document.querySelectorAll('.tool-btn').forEach(btn => {
            if (btn.getAttribute('data-tool') === tool) {
                btn.classList.add('active');
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-primary');
            } else {
                btn.classList.remove('active');
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-primary');
            }
        });

        // Hide all tool controls
        hideAllToolControls();

        // Show the selected tool controls
        switch(tool) {
            case 'scaling':
                scalingControls.classList.add('active');
                break;
            case 'rotation':
                rotationControls.classList.add('active');
                break;
            case 'crop':
                cropControls.classList.add('active');
                if (window.cropTool) window.cropTool.initCropPreview();
                break;
            case 'filter':
                filterControls.classList.add('active');
                break;
            case 'adjust':
                adjustControls.classList.add('active');
                break;
            case 'grid':
                gridControls.classList.add('active');
                break;
        }
    }

    function hideAllToolControls() {
        document.querySelectorAll('.editor-tab').forEach(tab => {
            tab.classList.remove('active');
        });
    }

    function showToolControls() {
        setActiveTool(window.currentTool);
    }

    function showResult(imageData) {
        // Remove any grid overlay
        if (window.gridTool) window.gridTool.removeGridOverlay();

        // Update result preview
        resultPreview.src = imageData;
        downloadBtn.href = imageData;

        // Update current image
        window.currentImage = imageData;

        // Hide tool controls
        hideAllToolControls();

        // Show result view
        imageResult.style.display = 'block';
    }

    // Initialize filter previews
    function initializeFilterPreviews(imgSrc) {
        // Set the original preview
        const previews = document.querySelectorAll('.filter-preview');
        previews.forEach(preview => {
            preview.src = imgSrc;
        });
    }

    // Reset all tools
    function resetAllTools() {
        // Reset tool-specific controls using their reset methods
        if (window.scaleTool) window.scaleTool.reset();
        if (window.rotateTool) window.rotateTool.reset();
        if (window.cropTool) window.cropTool.reset();
        if (window.filterTool) window.filterTool.reset();
        if (window.adjustTool) window.adjustTool.reset();
        if (window.gridTool) window.gridTool.reset();

        // Reset filter previews
        document.querySelectorAll('.filter-preview').forEach(preview => {
            if (preview.getAttribute('data-filter') === 'none') {
                preview.classList.add('active');
            } else {
                preview.classList.remove('active');
            }
        });
    }
});