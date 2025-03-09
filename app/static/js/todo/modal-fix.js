/**
 * Direct modal fix for todo application
 * This file provides a straightforward solution that directly addresses modal issues
 */

// Execute immediately when included
(function() {
    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Modal Fix: Initializing direct modal handling...');

        // Fix for "data-custom-modal" buttons
        setupDirectModalHandling();

        // Additional cleanup handlers
        setupModalCleanup();

        // Safety check after a delay (for any dynamically added elements)
        setTimeout(setupDirectModalHandling, 500);
    });

    /**
     * Set up direct handling for custom modal triggers
     */
    function setupDirectModalHandling() {
        // Get all buttons with data-custom-modal attribute
        document.querySelectorAll('[data-custom-modal]').forEach(function(button) {
            // Remove existing click listeners by cloning the button
            const newButton = button.cloneNode(true);
            if (button.parentNode) {
                button.parentNode.replaceChild(newButton, button);
            }

            // Add new click listener to directly show the modal
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                // Get the modal ID
                const modalId = this.getAttribute('data-custom-modal');
                if (!modalId) return;

                // First close any open modals
                document.querySelectorAll('.modal.show').forEach(function(openModal) {
                    try {
                        // Try using Bootstrap's API
                        const instance = bootstrap.Modal.getInstance(openModal);
                        if (instance) {
                            instance.hide();
                        } else {
                            // Manual fallback
                            openModal.classList.remove('show');
                            openModal.style.display = 'none';
                        }
                    } catch(e) {
                        // Just hide it manually
                        openModal.classList.remove('show');
                        openModal.style.display = 'none';
                    }
                });

                // Remove any leftover backdrops and body classes
                document.querySelectorAll('.modal-backdrop').forEach(function(backdrop) {
                    backdrop.remove();
                });
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';

                // Now show the target modal
                const targetModal = document.getElementById(modalId);
                if (!targetModal) {
                    console.error('Modal not found:', modalId);
                    return;
                }

                // Small delay before showing the modal
                setTimeout(function() {
                    // Try Bootstrap API first
                    try {
                        const modal = new bootstrap.Modal(targetModal);
                        modal.show();
                    } catch(e) {
                        console.warn('Error showing modal via Bootstrap:', e);

                        // Manual fallback if Bootstrap fails
                        targetModal.classList.add('show');
                        targetModal.style.display = 'block';

                        // Add backdrop manually
                        const backdrop = document.createElement('div');
                        backdrop.classList.add('modal-backdrop', 'fade', 'show');
                        document.body.appendChild(backdrop);
                        document.body.classList.add('modal-open');
                    }
                }, 50);
            });
        });

        // Also handle close buttons correctly
        document.querySelectorAll('.modal .btn-close, [data-bs-dismiss="modal"]').forEach(function(closeBtn) {
            // Remove existing handlers
            const newCloseBtn = closeBtn.cloneNode(true);
            if (closeBtn.parentNode) {
                closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
            }

            // Add new handler
            newCloseBtn.addEventListener('click', function(e) {
                e.preventDefault();

                // Find the parent modal
                const modal = this.closest('.modal');
                if (!modal) return;

                // Try closing with Bootstrap
                try {
                    const instance = bootstrap.Modal.getInstance(modal);
                    if (instance) {
                        instance.hide();
                        return;
                    }
                } catch(e) {
                    console.warn('Error closing modal via Bootstrap:', e);
                }

                // Fallback: close manually
                modal.classList.remove('show');
                modal.style.display = 'none';

                // Check if any modals are still open
                const openModals = document.querySelectorAll('.modal.show');
                if (openModals.length === 0) {
                    // Remove backdrop and body classes
                    document.querySelectorAll('.modal-backdrop').forEach(function(backdrop) {
                        backdrop.remove();
                    });
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }
            });
        });

        // Handle nested modals special case
        document.querySelectorAll('.modal [data-custom-modal]').forEach(function(nestedTrigger) {
            nestedTrigger.addEventListener('click', function() {
                // Close parent modal first
                const parentModal = this.closest('.modal');
                if (parentModal) {
                    try {
                        const instance = bootstrap.Modal.getInstance(parentModal);
                        if (instance) {
                            instance.hide();
                        }
                    } catch(e) {
                        // Just hide it manually
                        parentModal.classList.remove('show');
                        parentModal.style.display = 'none';
                    }
                }
            });
        });
    }

    /**
     * Set up periodic cleanup to fix any lingering modal issues
     */
    function setupModalCleanup() {
        // Periodically check for orphaned backdrops or body classes
        setInterval(function() {
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length === 0) {
                // No open modals, clean up
                document.querySelectorAll('.modal-backdrop').forEach(function(backdrop) {
                    backdrop.remove();
                });
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        }, 2000);

        // Add keyboard handler for Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const openModals = document.querySelectorAll('.modal.show');
                if (openModals.length > 0) {
                    // Get the last opened modal (top of the stack)
                    const topModal = openModals[openModals.length - 1];

                    // Try to close it with Bootstrap
                    try {
                        const instance = bootstrap.Modal.getInstance(topModal);
                        if (instance) {
                            instance.hide();
                            return;
                        }
                    } catch(e) {
                        console.warn('Error closing modal via Bootstrap:', e);
                    }

                    // Fallback: close manually
                    topModal.classList.remove('show');
                    topModal.style.display = 'none';

                    // Check if any modals are still open
                    const remainingModals = document.querySelectorAll('.modal.show');
                    if (remainingModals.length === 0) {
                        // Remove backdrop and body classes
                        document.querySelectorAll('.modal-backdrop').forEach(function(backdrop) {
                            backdrop.remove();
                        });
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    }
                }
            }
        });

        // Fix z-index issues for multiple modals
        document.querySelectorAll('.modal').forEach(function(modal, index) {
            modal.style.zIndex = 1050 + (index * 10);
        });

        // Fix backdrop z-index
        document.querySelectorAll('.modal-backdrop').forEach(function(backdrop, index) {
            backdrop.style.zIndex = 1040 + (index * 10);
        });
    }
})();