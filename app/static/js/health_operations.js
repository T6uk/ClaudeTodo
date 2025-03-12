/**
 * Health operations for workout, meal, and metrics management
 */

// Setup workout operations
function setupWorkoutOperations() {
    // View workout
    const viewWorkoutButtons = document.querySelectorAll('.view-workout-btn');
    viewWorkoutButtons.forEach(button => {
        button.addEventListener('click', function() {
            const workoutId = this.getAttribute('data-workout-id');
            fetch(`/health/workouts/${workoutId}`)
                .then(response => response.json())
                .then(data => {
                    // Fill modal with workout data
                    document.getElementById('viewWorkoutTitle').textContent = data.title;
                    document.getElementById('viewWorkoutType').textContent = data.workout_type.charAt(0).toUpperCase() + data.workout_type.slice(1);
                    document.getElementById('viewWorkoutDuration').textContent = data.duration;
                    document.getElementById('viewWorkoutIntensity').textContent = data.intensity ? data.intensity.charAt(0).toUpperCase() + data.intensity.slice(1) : 'Not specified';
                    document.getElementById('viewWorkoutCalories').textContent = data.calories_burned ? data.calories_burned + ' kcal' : 'Not specified';
                    document.getElementById('viewWorkoutDate').textContent = new Date(data.date).toLocaleString();

                    // Set notes
                    const notesEl = document.getElementById('viewWorkoutNotes').querySelector('p');
                    notesEl.textContent = data.notes || 'No notes provided.';

                    // Set up edit button
                    const editBtn = document.getElementById('editFromViewWorkoutBtn');
                    editBtn.setAttribute('data-workout-id', data.id);
                    editBtn.addEventListener('click', function() {
                        // Close view modal
                        bootstrap.Modal.getInstance(document.getElementById('viewWorkoutModal')).hide();

                        // Open edit modal with this workout's data
                        const editWorkoutBtn = document.querySelector(`.edit-workout-btn[data-workout-id="${data.id}"]`);
                        editWorkoutBtn.click();
                    });
                })
                .catch(error => console.error('Error fetching workout:', error));
        });
    });

    // Edit workout
    const editWorkoutButtons = document.querySelectorAll('.edit-workout-btn');
    editWorkoutButtons.forEach(button => {
        button.addEventListener('click', function() {
            const workoutId = this.getAttribute('data-workout-id');
            const form = document.getElementById('editWorkoutForm');
            form.action = `/health/workouts/${workoutId}/update`;

            fetch(`/health/workouts/${workoutId}`)
                .then(response => response.json())
                .then(data => {
                    // Fill form with workout data
                    document.getElementById('editWorkoutTitle').value = data.title;
                    document.getElementById('editWorkoutType').value = data.workout_type;
                    document.getElementById('editWorkoutDuration').value = data.duration;
                    document.getElementById('editWorkoutIntensity').value = data.intensity || '';
                    document.getElementById('editWorkoutCalories').value = data.calories_burned || '';

                    // Format date for datetime-local input
                    if (data.date) {
                        const date = new Date(data.date);
                        const formattedDate = date.toISOString().slice(0, 16);
                        document.getElementById('editWorkoutDate').value = formattedDate;
                    }

                    document.getElementById('editWorkoutNotes').value = data.notes || '';
                })
                .catch(error => console.error('Error fetching workout:', error));
        });
    });

    // Update workout
    const updateWorkoutBtn = document.getElementById('updateWorkoutBtn');
    if (updateWorkoutBtn) {
        updateWorkoutBtn.addEventListener('click', function() {
            document.getElementById('editWorkoutForm').submit();
        });
    }

    // Delete workout
    const deleteWorkoutButtons = document.querySelectorAll('.delete-workout-btn');
    deleteWorkoutButtons.forEach(button => {
        button.addEventListener('click', function() {
            const workoutId = this.getAttribute('data-workout-id');
            const workoutTitle = this.closest('.workout-item').querySelector('.workout-title').textContent.trim();

            document.getElementById('deleteWorkoutTitle').textContent = workoutTitle;
            document.getElementById('deleteWorkoutForm').action = `/health/workouts/${workoutId}/delete`;
        });
    });
}

// Setup meal operations
function setupMealOperations() {
    // Similar functionality as workout operations
    // ...implementation truncated for brevity
}

// Setup metrics operations
function setupMetricsOperations() {
    // Similar functionality as workout operations
    // ...implementation truncated for brevity
}

// Setup water intake functionality
function setupWaterIntake() {
    // Set up water intake quick add buttons
    const quickAmountButtons = document.querySelectorAll('.quick-amount');
    const amountInput = document.getElementById('amount');

    if (quickAmountButtons.length && amountInput) {
        quickAmountButtons.forEach(button => {
            button.addEventListener('click', function() {
                const amount = this.getAttribute('data-amount');
                amountInput.value = amount;
            });
        });
    }
}

// Search and filter functionality for workouts
function setupWorkoutFilters() {
    // Workout search functionality
    const workoutSearch = document.getElementById('workoutSearch');
    if (workoutSearch) {
        workoutSearch.addEventListener('input', filterWorkouts);
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
}

// Initialize all health tracking JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize workout operations
    setupWorkoutOperations();

    // Initialize meal operations
    setupMealOperations();

    // Initialize metrics operations
    setupMetricsOperations();

    // Initialize water intake functionality
    setupWaterIntake();

    // Initialize workout filters
    setupWorkoutFilters();

    // Initialize health charts
    setupHealthCharts();
});