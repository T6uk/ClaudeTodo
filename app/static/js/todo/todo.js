/**
 * Todo List Application JavaScript
 * This file handles all functionality for the todo list application
 * including modal handling, checkbox interactions, and UI enhancements.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize core functionality
    initializeModalHandling();
    initializeCheckboxInteractions();
    enhanceUIInteractions();
    setupFormHandling();
    setupAccessibility();
});

/**
 * Initialize modal handling functionality
 */
function initializeModalHandling() {
    fixModalInteractions();
    enhanceModalTriggers();
    setupDirectModalTriggers();
    setupModalCleanup();
}

/**
 * Fix interactions between modals and prevent common issues
 */
function fixModalInteractions() {
    // Properly handle closing modals
    document.querySelectorAll('.modal .btn-close, .modal [data-bs-dismiss="modal"]').forEach(button => {
        button.addEventListener('click', function() {
            const modalEl = this.closest('.modal');
            if (modalEl) {
                const modalInstance = bootstrap.Modal.getInstance(modalEl);
                if (modalInstance) {
                    modalInstance.hide();
                } else {
                    // Fallback if instance not accessible
                    modalEl.classList.remove('show');
                    modalEl.style.display = 'none';
                    document.body.classList.remove('modal-open');
                    document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
                }
            }
        });
    });

    // Ensure modal backdrop is properly removed
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length === 0) {
                document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                    backdrop.remove();
                });
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        });
    });

    // Make all modals static backdrop to prevent issues
    document.querySelectorAll('.modal').forEach(modal => {
        modal.setAttribute('data-bs-backdrop', 'static');
    });
}

/**
 * Enhance modal triggers to fix common Bootstrap modal issues
 */
function enhanceModalTriggers() {
    // Convert standard Bootstrap modal triggers to use our custom approach
    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(trigger => {
        const targetId = trigger.getAttribute('data-bs-target');
        if (targetId) {
            // Store the target ID as data-custom-modal instead
            trigger.setAttribute('data-custom-modal', targetId.replace('#', ''));

            // Remove the Bootstrap data attributes
            trigger.removeAttribute('data-bs-toggle');
            trigger.removeAttribute('data-bs-target');

            // Add our own event listener
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                const modalId = this.getAttribute('data-custom-modal');
                if (modalId) {
                    safelyShowModal(modalId);
                }
            });
        }
    });

    // Handle nested modals - prevent backdrop issues
    document.querySelectorAll('.modal').forEach(modal => {
        const nestedTriggers = modal.querySelectorAll('[data-bs-toggle="modal"]');
        nestedTriggers.forEach(trigger => {
            const targetId = trigger.getAttribute('data-bs-target');
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Close the current modal first
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                    
                    // Then show the target modal after a delay
                    setTimeout(() => {
                        const targetModal = document.querySelector(targetId);
                        if (targetModal) {
                            const newModalInstance = new bootstrap.Modal(targetModal);
                            newModalInstance.show();
                        }
                    }, 150);
                }
            });
        });
    });
}

/**
 * Set up custom modal triggers using our data-custom-modal attribute
 */
function setupDirectModalTriggers() {
    document.querySelectorAll('[data-custom-modal]').forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const targetModalId = this.getAttribute('data-custom-modal');
            if (targetModalId) {
                safelyShowModal(targetModalId);
            }
        });
    });
}

/**
 * Set up periodic modal cleanup to prevent orphaned backdrops
 */
function setupModalCleanup() {
    // Periodically check for orphaned backdrops
    setInterval(function() {
        const openModals = document.querySelectorAll('.modal.show');
        if (openModals.length === 0) {
            document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                backdrop.remove();
            });
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        }
    }, 3000);
}

/**
 * Initialize checkbox interactions for todo items
 */
function initializeCheckboxInteractions() {
    document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
        // Handle hover effects
        checkbox.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
        });

        checkbox.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });

        // Handle click with animation
        checkbox.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Create ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('checkbox-ripple');
            this.appendChild(ripple);
            
            // Get associated checkbox and form
            const checkboxId = this.getAttribute('for');
            const actualCheckbox = document.getElementById(checkboxId);
            
            if (actualCheckbox) {
                // Toggle visual state
                if (actualCheckbox.checked) {
                    this.classList.remove('checked');
                    this.innerHTML = '';
                } else {
                    this.classList.add('checked');
                    this.innerHTML = '<i class="bi bi-check"></i>';
                }
                
                // Toggle actual checkbox state
                actualCheckbox.checked = !actualCheckbox.checked;
                
                // Remove ripple and submit form after animation
                setTimeout(() => {
                    ripple.remove();
                    const formId = checkboxId.replace('todoCheck', 'statusForm');
                    const form = document.getElementById(formId);
                    if (form) form.submit();
                }, 300);
            }
        });
    });

    // Also enhance the status toggle in view modals
    document.querySelectorAll('.form-check-input[id^="viewModalCompleted"]').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const label = this.nextElementSibling;
            if (label) {
                label.textContent = this.checked ? 'Mark as incomplete' : 'Mark as completed';
            }
        });
    });
}

/**
 * Enhance UI interactions for better user experience
 */
function enhanceUIInteractions() {
    // Todo item hover effects
    document.querySelectorAll('.todo-item').forEach((item, index) => {
        // Stagger the animation
        setTimeout(() => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, 50);
        }, index * 50);
        
        // Hover effects for actions
        item.addEventListener('mouseenter', function() {
            const actions = this.querySelector('.todo-actions');
            if (actions) {
                actions.style.opacity = '1';
                actions.style.transform = 'translateX(0)';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            const actions = this.querySelector('.todo-actions');
            if (actions) {
                actions.style.opacity = '0';
                actions.style.transform = 'translateX(10px)';
            }
        });
    });

    // Due date highlighting
    highlightDueDates();

    // Initialize Bootstrap tooltips and popovers
    initializeBootstrapComponents();
}

/**
 * Highlight due dates based on proximity to today
 */
function highlightDueDates() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    document.querySelectorAll('.todo-meta div').forEach(meta => {
        if (meta.querySelector('.bi-calendar')) {
            const dateText = meta.textContent.trim();
            try {
                // Extract and parse the date
                const dateParts = dateText.split(' ');
                if (dateParts.length >= 3) {
                    const monthStr = dateParts[0];
                    const dayStr = dateParts[1].replace(',', '');
                    const yearStr = dateParts[2];
                    
                    const dateStr = `${monthStr} ${dayStr}, ${yearStr}`;
                    const dueDate = new Date(dateStr);
                    
                    // Check if due date is valid
                    if (!isNaN(dueDate.getTime())) {
                        if (dueDate < today) {
                            // Past due
                            meta.innerHTML = `<i class="bi bi-calendar me-1"></i> <span class="text-danger fw-bold">${dateText} (Overdue)</span>`;
                        } else if (
                            dueDate.getDate() === today.getDate() &&
                            dueDate.getMonth() === today.getMonth() &&
                            dueDate.getFullYear() === today.getFullYear()
                        ) {
                            // Due today
                            meta.innerHTML = `<i class="bi bi-calendar me-1"></i> <span class="text-warning fw-bold">${dateText} (Today)</span>`;
                        }
                    }
                }
            } catch (e) {
                console.warn('Could not parse date for highlighting', e);
            }
        }
    });
}

/**
 * Initialize Bootstrap tooltips and popovers
 */
function initializeBootstrapComponents() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Setup form handling and validation
 */
function setupFormHandling() {
    // Add visual feedback for form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains('btn-secondary')) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Saving...';
                submitBtn.disabled = true;
                
                // Re-enable button after 10 seconds in case of network issues
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                }, 10000);
            }
        });
    });

    // New task form validation
    const newTaskForm = document.querySelector('#newTaskModal form');
    if (newTaskForm) {
        newTaskForm.addEventListener('submit', function(e) {
            const titleInput = this.querySelector('#newTitle');
            if (titleInput && titleInput.value.trim() === '') {
                e.preventDefault();
                titleInput.classList.add('is-invalid');
                return false;
            }
        });
    }

    // General form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Setup accessibility features
 */
function setupAccessibility() {
    document.addEventListener('keydown', function(e) {
        // Close modals with Escape key
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(function(openModal) {
                const instance = bootstrap.Modal.getInstance(openModal);
                if (instance) instance.hide();
            });
        }
        
        // Allow interacting with todo checkboxes via keyboard
        if ((e.key === ' ' || e.key === 'Enter') &&
            document.activeElement.classList.contains('todo-checkbox')) {
            e.preventDefault();
            document.activeElement.click();
        }
    });

    // Make todo checkboxes focusable
    document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
        checkbox.setAttribute('tabindex', '0');
        checkbox.setAttribute('role', 'checkbox');
        checkbox.setAttribute('aria-checked', checkbox.classList.contains('checked') ? 'true' : 'false');
    });
}

/**
 * Safely show a modal by ID with robust error handling
 * @param {string} modalId - The ID of the modal to show (without #)
 */
function safelyShowModal(modalId) {
    try {
        // Get modal element
        const modalElement = document.getElementById(modalId);
        if (!modalElement) {
            console.error('Modal not found:', modalId);
            return;
        }

        // Clean up any existing modal state
        document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
        document.body.classList.remove('modal-open');
        
        // Close any open modals first
        document.querySelectorAll('.modal.show').forEach(function(openModal) {
            try {
                const instance = bootstrap.Modal.getInstance(openModal);
                if (instance) instance.hide();
            } catch (e) {
                // Just remove the modal if we can't hide it properly
                openModal.classList.remove('show');
                openModal.style.display = 'none';
            }
        });
        
        // Try to get existing instance
        let modalInstance;
        try {
            modalInstance = bootstrap.Modal.getInstance(modalElement);
            
            // If instance exists but might be broken, dispose it
            if (modalInstance) {
                modalInstance.dispose();
            }
        } catch (e) {
            console.warn('Error handling existing modal instance:', e);
        }
        
        // Create new modal instance and show it
        setTimeout(() => {
            try {
                const newInstance = new bootstrap.Modal(modalElement, {
                    backdrop: true,
                    keyboard: true,
                    focus: true
                });
                newInstance.show();
            } catch (err) {
                console.error('Failed to show modal:', err);
                
                // Fallback method: manual show
                modalElement.classList.add('show');
                modalElement.style.display = 'block';
                document.body.classList.add('modal-open');
                
                // Create backdrop manually
                const backdrop = document.createElement('div');
                backdrop.classList.add('modal-backdrop', 'fade', 'show');
                document.body.appendChild(backdrop);
            }
        }, 50); // Small delay helps prevent visual glitches
    } catch (e) {
        console.error('Error showing modal:', e);
    }
}