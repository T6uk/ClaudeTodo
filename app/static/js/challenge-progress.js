/**
 * Challenge progress visualization
 * Enhances the user experience when tracking challenge progress
 */
document.addEventListener('DOMContentLoaded', function() {
    // Color progress bars based on completion percentage
    const colorizeProgressBars = () => {
        const progressBars = document.querySelectorAll('.progress-bar');

        progressBars.forEach(bar => {
            const percentage = parseFloat(bar.getAttribute('aria-valuenow') || 0);

            // Skip if specific class is already set
            if (bar.classList.contains('bg-success') ||
                bar.classList.contains('bg-info') ||
                bar.classList.contains('bg-warning') ||
                bar.classList.contains('bg-danger')) {
                return;
            }

            // Remove existing color classes
            bar.classList.remove('bg-success', 'bg-info', 'bg-primary', 'bg-warning', 'bg-danger');

            // Add appropriate color class
            if (percentage >= 100) {
                bar.classList.add('bg-success');
            } else if (percentage >= 75) {
                bar.classList.add('bg-info');
            } else if (percentage >= 50) {
                bar.classList.add('bg-primary');
            } else if (percentage >= 25) {
                bar.classList.add('bg-warning');
            } else {
                bar.classList.add('bg-danger');
            }
        });
    };

    // Progress update modal functionality
    const setupProgressModal = () => {
        const updateProgressButtons = document.querySelectorAll('.update-progress-btn');

        updateProgressButtons.forEach(button => {
            button.addEventListener('click', function() {
                const challengeId = this.getAttribute('data-challenge-id');
                const currentValue = parseFloat(this.getAttribute('data-challenge-current')) || 0;
                const targetValue = parseFloat(this.getAttribute('data-challenge-target')) || 100;
                const unit = this.getAttribute('data-challenge-unit') || '';

                // Set up progress value display
                updateProgressValueDisplay(currentValue, targetValue, unit);

                // Add animation to the progress display
                animateProgressUpdate(currentValue, targetValue);
            });
        });

        // Set up range input synchronization with numeric input
        const rangeInput = document.getElementById('progress_value');
        const numericInput = document.getElementById('progress_value_numeric');

        if (rangeInput && numericInput) {
            rangeInput.addEventListener('input', function() {
                numericInput.value = this.value;
                document.getElementById('progressCurrentValue').textContent = this.value;
            });

            numericInput.addEventListener('input', function() {
                rangeInput.value = this.value;
                document.getElementById('progressCurrentValue').textContent = this.value;
            });
        }
    };

    // Update progress value display
    const updateProgressValueDisplay = (current, target, unit) => {
        const progressValueEl = document.getElementById('progressCurrentValue');
        const progressTargetEl = document.getElementById('progressTarget');
        const progressUnitEl = document.getElementById('progressUnit');
        const progressUnitStartEl = document.getElementById('progressUnitStart');
        const progressUnitEndEl = document.getElementById('progressUnitEnd');
        const progressUnitAddonEl = document.getElementById('progressUnitAddon');

        if (progressValueEl) progressValueEl.textContent = current;
        if (progressTargetEl) progressTargetEl.textContent = target;

        // Set units
        [progressUnitEl, progressUnitStartEl, progressUnitEndEl, progressUnitAddonEl].forEach(el => {
            if (el) el.textContent = unit;
        });
    };

    // Animate progress update
    const animateProgressUpdate = (current, target) => {
        const rangeInput = document.getElementById('progress_value');
        if (!rangeInput) return;

        // Apply pulse animation to slider thumb
        rangeInput.classList.add('pulse-thumb');

        // Remove the animation class after a delay
        setTimeout(() => {
            rangeInput.classList.remove('pulse-thumb');
        }, 1000);
    };

    // Calculate time remaining for challenges
    const updateTimeRemaining = () => {
        const challenges = document.querySelectorAll('.challenge-item[data-challenge-id]');
        const now = new Date();

        challenges.forEach(challenge => {
            const endDateEl = challenge.querySelector('.challenge-meta span:nth-child(2)');
            if (!endDateEl) return;

            const endDateText = endDateEl.textContent;
            const endDateMatch = endDateText.match(/Ends: (.*)/);

            if (endDateMatch) {
                const endDate = new Date(endDateMatch[1]);
                const daysRemaining = Math.ceil((endDate - now) / (1000 * 60 * 60 * 24));

                if (daysRemaining > 0) {
                    endDateEl.innerHTML = `<i class="fas fa-hourglass-half me-1"></i> ${daysRemaining} days left`;
                } else {
                    endDateEl.innerHTML = `<i class="fas fa-hourglass-end me-1"></i> <span class="text-danger">Deadline passed</span>`;
                }
            }
        });
    };

    // Add tooltip to explain progress updates
    const addProgressTooltips = () => {
        const progressElements = document.querySelectorAll('.progress');

        progressElements.forEach(el => {
            // Add tooltip if Bootstrap is available
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                new bootstrap.Tooltip(el, {
                    title: 'Track your progress towards the target goal',
                    placement: 'top'
                });
            }
        });
    };

    // Run all the enhancement functions
    colorizeProgressBars();
    setupProgressModal();
    updateTimeRemaining();
    addProgressTooltips();

    // Add some CSS for the pulse animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse-thumb {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        
        .pulse-thumb::-webkit-slider-thumb {
            animation: pulse-thumb 1s ease infinite;
        }
        
        .pulse-thumb::-moz-range-thumb {
            animation: pulse-thumb 1s ease infinite;
        }
    `;
    document.head.appendChild(style);
});