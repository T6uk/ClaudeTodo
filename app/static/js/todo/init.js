/**
 * Todo Application - Main Initialization
 * This file coordinates the initialization of all Todo components
 */

/**
 * The TodoApp namespace coordinates the initialization and integration of all Todo components
 */
window.TodoApp = (function() {
    // Store initialization state
    let _initialized = false;

    /**
     * Initialize the Todo Application
     */
    function init() {
        if (_initialized) return;

        console.log('Initializing Todo Application...');

        // Initialize modal utilities first (highest priority)
        if (window.TodoModalUtils) {
            window.TodoModalUtils.init();
            window.TodoModalUtils.setupCustomModalTriggers();
        }

        // Initialize checkbox handling
        if (window.TodoCheckboxHandler) {
            window.TodoCheckboxHandler.init();
        }

        // Add animation to todo items
        animateTodoItems();

        // Fix modal trigger buttons
        fixModalTriggers();

        // Set up keyboard shortcuts
        setupKeyboardShortcuts();

        // Initialize all other features
        setupUIEnhancements();

        _initialized = true;
        console.log('Todo Application initialized successfully');
    }

    /**
     * Animate todo items with staggered fade-in
     */
    function animateTodoItems() {
        document.querySelectorAll('.todo-item').forEach((item, index) => {
            // Set initial state
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';

            // Animate with staggered delay
            setTimeout(() => {
                item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, 50 + (index * 50)); // Stagger by 50ms per item
        });
    }

    /**
     * Fix modal trigger buttons to use our custom handling
     */
    function fixModalTriggers() {
        // Replace standard Bootstrap triggers with our custom implementation
        document.querySelectorAll('[data-bs-toggle="modal"]').forEach(button => {
            const targetId = button.getAttribute('data-bs-target');
            if (targetId) {
                // Convert to data-custom-modal
                button.setAttribute('data-custom-modal', targetId.replace('#', ''));
                button.removeAttribute('data-bs-toggle');
                button.removeAttribute('data-bs-target');

                // Replace with new event listener
                const newButton = button.cloneNode(true);
                button.parentNode.replaceChild(newButton, button);

                newButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    const modalId = this.getAttribute('data-custom-modal');
                    if (modalId && window.TodoModalUtils) {
                        window.TodoModalUtils.showModal(modalId);
                    }
                });
            }
        });
    }

    /**
     * Set up keyboard shortcuts for common actions
     */
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Alt+N for new task
            if (e.altKey && e.key === 'n') {
                e.preventDefault();
                if (window.TodoModalUtils) {
                    window.TodoModalUtils.showModal('newTaskModal');
                }
            }

            // Escape to close modals
            if (e.key === 'Escape') {
                if (window.TodoModalUtils) {
                    window.TodoModalUtils.closeAllModals();
                }
            }
        });
    }

    /**
     * Set up UI enhancements for better user experience
     */
    function setupUIEnhancements() {
        // Add hover effects to action buttons
        document.querySelectorAll('.todo-action-btn').forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
            });

            button.addEventListener('mouseleave', function() {
                this.style.transform = '';
                this.style.boxShadow = '';
            });
        });

        // Enhance form submissions with loading indicators
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function() {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.disabled && !submitBtn.classList.contains('btn-secondary')) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Saving...';
                    submitBtn.disabled = true;

                    // Safety timeout to prevent button from staying disabled forever
                    setTimeout(() => {
                        if (submitBtn.disabled) {
                            submitBtn.innerHTML = originalText;
                            submitBtn.disabled = false;
                        }
                    }, 8000);
                }
            });
        });

        // Highlight due dates
        highlightDueDates();
    }

    /**
     * Highlight due dates that are today or overdue
     */
    function highlightDueDates() {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        document.querySelectorAll('.todo-meta').forEach(meta => {
            const dateElements = meta.querySelectorAll('div');

            dateElements.forEach(elem => {
                if (elem.querySelector('.bi-calendar')) {
                    const dateText = elem.textContent.trim();

                    try {
                        // Parse date from text
                        const dateMatch = dateText.match(/(\w+)\s+(\d+),\s+(\d+)/);
                        if (dateMatch) {
                            const [_, month, day, year] = dateMatch;
                            const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                            const monthIndex = monthNames.findIndex(m => month.includes(m));

                            if (monthIndex !== -1) {
                                const dueDate = new Date(year, monthIndex, parseInt(day));

                                if (dueDate < today) {
                                    // Overdue
                                    elem.innerHTML = `<i class="bi bi-calendar-x me-1"></i> <span class="text-danger fw-bold">${dateText} (Overdue)</span>`;
                                } else if (
                                    dueDate.getDate() === today.getDate() &&
                                    dueDate.getMonth() === today.getMonth() &&
                                    dueDate.getFullYear() === today.getFullYear()
                                ) {
                                    // Due today
                                    elem.innerHTML = `<i class="bi bi-calendar-check me-1"></i> <span class="text-warning fw-bold">${dateText} (Today)</span>`;
                                }
                            }
                        }
                    } catch (e) {
                        console.warn('Error parsing date:', e);
                    }
                }
            });
        });
    }

    /**
     * Public API
     */
    return {
        init: init,
        reinitialize: function() {
            _initialized = false;
            init();
        }
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the Todo Application
    window.TodoApp.init();

    // Also set up a safety check to reinitialize after 1 second
    // This helps with pages where content might load dynamically
    setTimeout(() => {
        window.TodoApp.reinitialize();
    }, 1000);
});