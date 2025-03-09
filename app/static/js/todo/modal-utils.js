/**
 * Modal utilities for reliable modal handling
 * This file provides additional utility functions to ensure modals work correctly in all situations
 */

/**
 * The TodoModalUtils namespace contains specialized functions for handling Bootstrap modals
 * with enhanced reliability and error prevention
 */
window.TodoModalUtils = (function() {
    // Private variables
    let _activeModals = [];
    let _cleanupInterval = null;

    /**
     * Initialize the modal utilities
     */
    function init() {
        _setupGlobalHandlers();
        _monitorExistingModals();
        _startCleanupInterval();

        console.log('TodoModalUtils initialized');
    }

    /**
     * Set up global handlers for modal events
     */
    function _setupGlobalHandlers() {
        // Track when modals are shown
        document.addEventListener('shown.bs.modal', function(e) {
            const modalElement = e.target;
            if (modalElement && !_activeModals.includes(modalElement.id)) {
                _activeModals.push(modalElement.id);
            }

            // Adjust z-indices for proper stacking
            _adjustModalZIndices();
        });

        // Track when modals are hidden
        document.addEventListener('hidden.bs.modal', function(e) {
            const modalElement = e.target;
            if (modalElement) {
                _activeModals = _activeModals.filter(id => id !== modalElement.id);

                // Only remove all backdrops if no modals are active
                if (_activeModals.length === 0) {
                    _cleanupModalBackdrops();
                }
            }
        });

        // Handle escape key for closing modals
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && _activeModals.length > 0) {
                const lastModalId = _activeModals[_activeModals.length - 1];
                if (lastModalId) {
                    const modalElement = document.getElementById(lastModalId);
                    if (modalElement) {
                        closeModal(modalElement);
                    }
                }
            }
        });
    }

    /**
     * Monitor existing modals to ensure they have proper configuration
     */
    function _monitorExistingModals() {
        document.querySelectorAll('.modal').forEach(function(modal) {
            // Ensure modals have fade class for animations
            if (!modal.classList.contains('fade')) {
                modal.classList.add('fade');
            }

            // Make sure all modals have IDs for tracking
            if (!modal.id) {
                modal.id = 'modal-' + Math.floor(Math.random() * 1000000);
            }

            // Add failsafe close handler to all close buttons
            modal.querySelectorAll('[data-bs-dismiss="modal"]').forEach(function(closeBtn) {
                closeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    closeModal(modal);
                });
            });
        });
    }

    /**
     * Start interval to periodically clean up modal artifacts
     */
    function _startCleanupInterval() {
        if (_cleanupInterval) {
            clearInterval(_cleanupInterval);
        }

        _cleanupInterval = setInterval(function() {
            _cleanupOrphanedBackdrops();
            _fixBodyClasses();
        }, 3000);
    }

    /**
     * Adjust z-indices for multiple open modals
     */
    function _adjustModalZIndices() {
        document.querySelectorAll('.modal.show').forEach(function(modal, index) {
            // Each modal gets a higher z-index
            modal.style.zIndex = 1050 + (index * 10);

            // Find the backdrop for this modal if possible
            const backdrops = document.querySelectorAll('.modal-backdrop');
            if (backdrops[index]) {
                backdrops[index].style.zIndex = 1040 + (index * 10);
            }
        });
    }

    /**
     * Clean up orphaned backdrops (those without a corresponding open modal)
     */
    function _cleanupOrphanedBackdrops() {
        const openModals = document.querySelectorAll('.modal.show');
        const backdrops = document.querySelectorAll('.modal-backdrop');

        if (openModals.length === 0 && backdrops.length > 0) {
            _cleanupModalBackdrops();
        } else if (backdrops.length > openModals.length) {
            // Too many backdrops - remove excess ones
            for (let i = openModals.length; i < backdrops.length; i++) {
                backdrops[i].remove();
            }
        }
    }

    /**
     * Clean up all modal backdrops
     */
    function _cleanupModalBackdrops() {
        document.querySelectorAll('.modal-backdrop').forEach(function(backdrop) {
            backdrop.remove();
        });
    }

    /**
     * Fix body classes that can get stuck
     */
    function _fixBodyClasses() {
        const openModals = document.querySelectorAll('.modal.show');
        if (openModals.length === 0) {
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        }
    }

    /**
     * Recreate a modal instance to fix potential issues
     * @param {HTMLElement|string} modal - The modal element or its ID
     * @return {Object} The new modal instance
     */
    function recreateModalInstance(modal) {
        const modalElement = typeof modal === 'string' ? document.getElementById(modal) : modal;
        if (!modalElement) return null;

        try {
            // Try to get and dispose of any existing instance
            const existingModal = bootstrap.Modal.getInstance(modalElement);
            if (existingModal) {
                existingModal.dispose();
            }
        } catch (e) {
            console.warn('Error disposing existing modal:', e);
        }

        // Create and return a fresh instance
        return new bootstrap.Modal(modalElement, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
    }

    /**
     * Safely show a modal, handling all edge cases
     * @param {HTMLElement|string} modal - The modal element or its ID
     */
    function showModal(modal) {
        const modalElement = typeof modal === 'string' ? document.getElementById(modal) : modal;
        if (!modalElement) {
            console.error('Modal not found:', modal);
            return;
        }

        try {
            // Clean up state and close any open modals first
            document.querySelectorAll('.modal.show').forEach(function(openModal) {
                try {
                    const instance = bootstrap.Modal.getInstance(openModal);
                    if (instance) instance.hide();
                } catch (e) {
                    console.warn('Error hiding open modal:', e);
                    // Fallback: manual hide
                    openModal.classList.remove('show');
                    openModal.style.display = 'none';
                }
            });

            // Small delay to ensure previous modals are fully closed
            setTimeout(function() {
                try {
                    // Create new instance and show it
                    const modalInstance = recreateModalInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.show();
                    }
                } catch (err) {
                    console.error('Error showing modal:', err);

                    // Manual fallback method if Bootstrap modal fails
                    modalElement.style.display = 'block';
                    modalElement.classList.add('show');
                    document.body.classList.add('modal-open');

                    // Create backdrop manually
                    const backdrop = document.createElement('div');
                    backdrop.classList.add('modal-backdrop', 'fade', 'show');
                    document.body.appendChild(backdrop);
                }
            }, 100);
        } catch (e) {
            console.error('Fatal error showing modal:', e);
        }
    }

    /**
     * Safely close a modal, handling all edge cases
     * @param {HTMLElement|string} modal - The modal element or its ID
     */
    function closeModal(modal) {
        const modalElement = typeof modal === 'string' ? document.getElementById(modal) : modal;
        if (!modalElement) return;

        try {
            // Try bootstrap method first
            const instance = bootstrap.Modal.getInstance(modalElement);
            if (instance) {
                instance.hide();
                return;
            }

            // Fallback if no instance available
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';

            // Only remove backdrop and body classes if this is the last modal
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length === 0) {
                document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        } catch (e) {
            console.warn('Error closing modal:', e);

            // Manual force close as last resort
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
        }
    }

    /**
     * Close all open modals
     */
    function closeAllModals() {
        document.querySelectorAll('.modal.show').forEach(function(modal) {
            closeModal(modal);
        });
    }

    /**
     * Setup custom modal triggers that bypass Bootstrap's data attributes
     */
    function setupCustomModalTriggers() {
        document.querySelectorAll('[data-custom-modal]').forEach(function(trigger) {
            // Remove existing click listeners first
            const newTrigger = trigger.cloneNode(true);
            trigger.parentNode.replaceChild(newTrigger, trigger);

            // Add new click listener
            newTrigger.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const targetModalId = this.getAttribute('data-custom-modal');
                if (targetModalId) {
                    showModal(targetModalId);
                }
            });
        });
    }

    // Initialize immediately when script loads
    document.addEventListener('DOMContentLoaded', init);

    // Return public methods
    return {
        init: init,
        showModal: showModal,
        closeModal: closeModal,
        closeAllModals: closeAllModals,
        recreateModalInstance: recreateModalInstance,
        setupCustomModalTriggers: setupCustomModalTriggers
    };
})();