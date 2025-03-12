// app/static/js/workout.js (update)

/**
 * Enhanced workout management functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Workout search functionality
    const workoutSearch = document.getElementById('workoutSearch');
    if (workoutSearch) {
        workoutSearch.addEventListener('input', function() {
            filterWorkouts();
        });
    }

    // Workout type filtering
    const filterButtons = document.querySelectorAll('.workout-filter');
    if (filterButtons.length) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));

                // Add active class to clicked button
                this.classList.add('active');

                filterWorkouts();
            });
        });
    }

    // Combined filtering function for search and type filters
    function filterWorkouts() {
        const workouts = document.querySelectorAll('.workout-item');
        const searchText = workoutSearch ? workoutSearch.value.toLowerCase() : '';
        const activeFilterButton = document.querySelector('.workout-filter.active');
        const filterType = activeFilterButton ? activeFilterButton.getAttribute('data-filter') : 'all';

        workouts.forEach(workout => {
            const title = workout.querySelector('.workout-title').textContent.toLowerCase();
            const meta = workout.querySelector('.workout-meta').textContent.toLowerCase();
            const notes = workout.querySelector('p') ? workout.querySelector('p').textContent.toLowerCase() : '';
            const workoutType = workout.getAttribute('data-workout-type');

            // Search text filter
            const matchesSearch = searchText === '' ||
                title.includes(searchText) ||
                meta.includes(searchText) ||
                notes.includes(searchText);

            // Type filter
            let matchesType = false;
            if (filterType === 'all') {
                matchesType = true;
            } else if (filterType === 'cardio' && workoutType === 'cardio') {
                matchesType = true;
            } else if (filterType === 'strength' && workoutType === 'strength') {
                matchesType = true;
            } else if (filterType === 'other' && workoutType !== 'cardio' && workoutType !== 'strength') {
                matchesType = true;
            }

            // Apply visibility based on both filters
            workout.style.display = (matchesSearch && matchesType) ? '' : 'none';
        });
    }

    // Initialize filtering on page load
    if (document.querySelector('.workout-filter')) {
        filterWorkouts();
    }

    // Update workout progress display
    function updateWorkoutProgress() {
        const totalExercises = document.querySelectorAll('.exercise-checkbox').length;
        const completedExercises = document.querySelectorAll('.exercise-checkbox:checked').length;

        if (totalExercises > 0) {
            const progressPercentage = (completedExercises / totalExercises) * 100;
            const progressBar = document.querySelector('.workout-progress-bar');
            const progressText = document.querySelector('.workout-progress-text');

            if (progressBar) {
                progressBar.style.width = `${progressPercentage}%`;
            }

            if (progressText) {
                progressText.textContent = `${completedExercises} of ${totalExercises} exercises completed (${Math.round(progressPercentage)}%)`;
            }
        }
    }

    // Initialize progress on page load
    if (document.querySelectorAll('.exercise-checkbox').length) {
        updateWorkoutProgress();
    }
});