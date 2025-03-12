// app/static/js/dashboard_customize.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize sortable container for drag-and-drop
    const widgetsContainer = document.getElementById('dashboardWidgetsContainer');
    let sortable = Sortable.create(widgetsContainer, {
        animation: 150,
        handle: '.handle',
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        onEnd: function(evt) {
            // Update positions after drag
            updateWidgetPositions();
        }
    });

    // Function to update all widget positions
    function updateWidgetPositions() {
        const widgets = document.querySelectorAll('.dashboard-widget');
        const positions = [];

        widgets.forEach((widget, index) => {
            const widgetId = widget.getAttribute('data-widget-id');
            widget.setAttribute('data-position', index);
            positions.push({
                id: widgetId,
                position: index
            });
        });

        return positions;
    }

    // Save layout button
    const saveLayoutBtn = document.getElementById('saveLayoutBtn');
    saveLayoutBtn.addEventListener('click', function() {
        const positions = updateWidgetPositions();

        // Send updated positions to server
        fetch('/dashboard/widgets/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(positions)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                const alertHtml = `
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        <i class="fas fa-check-circle me-2"></i>
                        Dashboard layout saved successfully.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
                document.querySelector('.container').insertAdjacentHTML('afterbegin', alertHtml);

                // Auto dismiss alert after 3 seconds
                setTimeout(() => {
                    const alert = document.querySelector('.alert');
                    if (alert) {
                        const bsAlert = new bootstrap.Alert(alert);
                        bsAlert.close();
                    }
                }, 3000);
            } else {
                console.error('Error saving layout:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Toggle widget enabled/disabled
const toggleButtons = document.querySelectorAll('.widget-toggle');
toggleButtons.forEach(btn => {
    btn.addEventListener('click', function() {
        const widget = this.closest('.dashboard-widget');
        const widgetId = widget.getAttribute('data-widget-id');
        const currentlyEnabled = widget.getAttribute('data-enabled') === 'true';

        fetch(`/dashboard/widgets/${widgetId}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI
                const icon = this.querySelector('i');
                if (data.enabled) {
                    // Widget is now enabled
                    widget.setAttribute('data-enabled', 'true');
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                    this.setAttribute('title', 'Disable Widget');
                } else {
                    // Widget is now disabled
                    widget.setAttribute('data-enabled', 'false');
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                    this.setAttribute('title', 'Enable Widget');
                }
            }
        })
        .catch(error => {
            console.error('Error toggling widget:', error);
        });
    });
});

    // Resize widget
    const resizeButtons = document.querySelectorAll('.widget-resize');
    resizeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const widget = this.closest('.dashboard-widget');
            const widgetId = widget.getAttribute('data-widget-id');
            const newSize = this.getAttribute('data-size');

            fetch(`/dashboard/widgets/${widgetId}/resize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ size: newSize })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    widget.classList.remove('widget-small', 'widget-medium', 'widget-large');
                    widget.classList.add(`widget-${newSize}`);
                }
            })
            .catch(error => {
                console.error('Error resizing widget:', error);
            });
        });
    });

    // Delete widget
    const deleteButtons = document.querySelectorAll('.widget-delete');
    let widgetToDelete = null;
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));

    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const widget = this.closest('.dashboard-widget');
            widgetToDelete = widget.getAttribute('data-widget-id');
            confirmDeleteModal.show();
        });
    });

    confirmDeleteBtn.addEventListener('click', function() {
        if (!widgetToDelete) return;

        fetch(`/dashboard/widgets/${widgetToDelete}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove widget from DOM
                const widget = document.querySelector(`.dashboard-widget[data-widget-id="${widgetToDelete}"]`);
                if (widget) {
                    widget.remove();
                }
                confirmDeleteModal.hide();
            }
        })
        .catch(error => {
            console.error('Error deleting widget:', error);
        });
    });

    // Add new widget
    const addWidgetBtns = document.querySelectorAll('.add-widget-btn');
    addWidgetBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const widgetType = this.getAttribute('data-widget-type');

            fetch('/dashboard/widgets/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ widget_type: widgetType })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload page to show new widget
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error adding widget:', error);
            });
        });
    });
});