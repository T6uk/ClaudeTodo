/**
 * Enhanced Todo Checkbox Interactions
 * This file provides advanced functionality for todo checkboxes with animations and effects
 */

window.TodoCheckboxHandler = (function() {
    // Track if already initialized
    let _initialized = false;

    /**
     * Initialize the checkbox handler with all enhancements
     */
    function init() {
        if (_initialized) return;

        setupCheckboxes();
        setupStatusToggles();
        setupAccessibility();

        _initialized = true;
        console.log('TodoCheckboxHandler initialized');
    }

    /**
     * Setup the checkbox interactions and animations
     */
    function setupCheckboxes() {
        document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
            // Add visual hover effects
            checkbox.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.1)';
                this.style.boxShadow = '0 0 0 4px rgba(78, 115, 223, 0.1)';
            });

            checkbox.addEventListener('mouseleave', function() {
                this.style.transform = '';
                this.style.boxShadow = '';
            });

            // Add click handling with animations
            checkbox.addEventListener('click', function(e) {
                e.preventDefault();
                toggleCheckboxWithEffects(this);
            });
        });
    }

    /**
     * Toggle a checkbox with visual effects and form submission
     * @param {HTMLElement} checkbox - The checkbox element to toggle
     */
    function toggleCheckboxWithEffects(checkbox) {
        // Create ripple effect animation
        addRippleEffect(checkbox);

        // Get the associated checkbox input
        const checkboxId = checkbox.getAttribute('for');
        const actualCheckbox = document.getElementById(checkboxId);

        if (actualCheckbox) {
            // Toggle visual state
            if (actualCheckbox.checked) {
                checkbox.classList.remove('checked');
                checkbox.innerHTML = '';
                checkbox.setAttribute('aria-checked', 'false');
            } else {
                checkbox.classList.add('checked');
                checkbox.innerHTML = '<i class="bi bi-check"></i>';
                checkbox.setAttribute('aria-checked', 'true');
            }

            // Toggle actual checkbox state
            actualCheckbox.checked = !actualCheckbox.checked;

            // Submit the form after animation completes
            setTimeout(() => {
                const formId = checkboxId.replace('todoCheck', 'statusForm');
                const form = document.getElementById(formId);
                if (form) {
                    try {
                        form.submit();
                    } catch (e) {
                        console.error('Error submitting form:', e);

                        // Fallback - create and submit form manually
                        const todoId = checkboxId.replace('todoCheck', '');
                        submitStatusUpdate(todoId, actualCheckbox.checked);
                    }
                }
            }, 300);
        }
    }

    /**
     * Add ripple effect animation to an element
     * @param {HTMLElement} element - The element to add the effect to
     */
    function addRippleEffect(element) {
        // Create and configure the ripple element
        const ripple = document.createElement('span');
        ripple.classList.add('checkbox-ripple');

        // Add to the element
        element.appendChild(ripple);

        // Remove ripple after animation
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * Fallback method to submit status updates
     * @param {string} todoId - The ID of the todo
     * @param {boolean} completed - Whether the todo is completed
     */
    function submitStatusUpdate(todoId, completed) {
        // Create a form programmatically
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/todo/${todoId}/update-status`;

        // Add CSRF token if available
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrf_token';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
        }

        // Add completed state
        if (completed) {
            const completedInput = document.createElement('input');
            completedInput.type = 'hidden';
            completedInput.name = 'completed';
            completedInput.value = 'on';
            form.appendChild(completedInput);
        }

        // Submit the form
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    }

    /**
     * Setup status toggles in modal views
     */
    function setupStatusToggles() {
        document.querySelectorAll('.form-check-input[id^="viewModalCompleted"]').forEach(toggle => {
            toggle.addEventListener('change', function() {
                // Update the label
                const label = this.nextElementSibling;
                if (label) {
                    label.textContent = this.checked ? 'Mark as incomplete' : 'Mark as completed';
                }

                // Add visual feedback
                const parent = this.closest('.form-check');
                if (parent) {
                    parent.style.transition = 'background-color 0.3s ease';
                    parent.style.backgroundColor = 'rgba(78, 115, 223, 0.1)';

                    setTimeout(() => {
                        parent.style.backgroundColor = '';
                    }, 500);
                }
            });
        });
    }

    /**
     * Setup accessibility features for checkboxes
     */
    function setupAccessibility() {
        // Make todo checkboxes keyboard accessible
        document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
            checkbox.setAttribute('tabindex', '0');
            checkbox.setAttribute('role', 'checkbox');
            checkbox.setAttribute('aria-checked', checkbox.classList.contains('checked') ? 'true' : 'false');

            // Add keyboard event handler
            checkbox.addEventListener('keydown', function(e) {
                if (e.key === ' ' || e.key === 'Enter') {
                    e.preventDefault();
                    toggleCheckboxWithEffects(this);
                }
            });
        });
    }

    /**
     * Public API
     */
    return {
        init: init,
        setupCheckboxes: setupCheckboxes,
        toggleCheckbox: toggleCheckboxWithEffects
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.TodoCheckboxHandler.init();
});