/**
 * Health charts initialization
 * Handles rendering and updating all charts in the health tracking module
 */

function setupHealthCharts() {
    // Workout Type Chart
    initializeWorkoutTypeChart();

    // Nutrition charts
    initializeNutritionCharts();

    // Activity charts
    initializeActivityCharts();

    // Weight and metrics charts
    initializeWeightChart();
}

/**
 * Initialize the workout type distribution chart
 */
function initializeWorkoutTypeChart() {
    const workoutTypeChart = document.getElementById('workoutTypeChart');
    if (!workoutTypeChart) return;

    // Extract data from hidden element
    const workoutTypesData = JSON.parse(document.getElementById('workout-types-data').textContent);
    const labels = Object.keys(workoutTypesData);
    const data = Object.values(workoutTypesData);

    // Workout type colors
    const typeColors = {
        'cardio': 'rgba(87, 167, 115, 0.8)',
        'strength': 'rgba(128, 144, 178, 0.8)',
        'flexibility': 'rgba(183, 201, 232, 0.8)',
        'sports': 'rgba(161, 178, 212, 0.8)',
        'hiit': 'rgba(215, 100, 100, 0.8)',
        'crossfit': 'rgba(243, 201, 105, 0.8)',
        'yoga': 'rgba(196, 214, 232, 0.8)',
        'other': 'rgba(108, 117, 125, 0.8)'
    };

    // Create colors array
    const colors = labels.map(label => typeColors[label] || 'rgba(108, 117, 125, 0.8)');

    // Create workout types chart
    new Chart(workoutTypeChart, {
        type: 'doughnut',
        data: {
            labels: labels.map(label => label.charAt(0).toUpperCase() + label.slice(1)),
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Workout Types Distribution'
                }
            }
        }
    });
}

/**
 * Initialize nutrition-related charts
 */
function initializeNutritionCharts() {
    // Main nutrition chart in analytics tab
    const nutritionChart = document.getElementById('nutritionChart');
    if (nutritionChart) {
        // Extract nutrition data
        const nutritionData = JSON.parse(document.getElementById('nutrition-data').textContent);
        const protein = nutritionData.protein;
        const carbs = nutritionData.carbs;
        const fat = nutritionData.fat;

        // Create pie chart for macronutrients
        new Chart(nutritionChart, {
            type: 'pie',
            data: {
                labels: ['Protein', 'Carbs', 'Fat'],
                datasets: [{
                    data: [protein, carbs, fat],
                    backgroundColor: [
                        'rgba(87, 167, 115, 0.8)',
                        'rgba(183, 201, 232, 0.8)',
                        'rgba(215, 100, 100, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Macronutrient Distribution (g)'
                    }
                }
            }
        });
    }

    // Macros doughnut chart in nutrition tab
    const macrosChart = document.getElementById('macrosChart');
    if (macrosChart) {
        // Extract nutrition data
        const nutritionData = JSON.parse(document.getElementById('nutrition-data').textContent);
        const protein = nutritionData.protein;
        const carbs = nutritionData.carbs;
        const fat = nutritionData.fat;
        const total = protein + carbs + fat;

        // Create doughnut chart for macronutrients
        new Chart(macrosChart, {
            type: 'doughnut',
            data: {
                labels: ['Protein', 'Carbs', 'Fat'],
                datasets: [{
                    data: [protein, carbs, fat],
                    backgroundColor: [
                        'rgba(87, 167, 115, 0.8)',
                        'rgba(183, 201, 232, 0.8)',
                        'rgba(215, 100, 100, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw.toFixed(1);
                                const percentage = total > 0 ? Math.round(context.raw / total * 100) : 0;
                                return `${context.label}: ${value}g (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Calorie chart
    const calorieChart = document.getElementById('calorieChart');
    if (calorieChart) {
        // Daily calorie data
        const calorieDates = JSON.parse(document.getElementById('calorie-dates-data').textContent);
        const calorieData = JSON.parse(document.getElementById('calorie-data').textContent);

        new Chart(calorieChart, {
            type: 'line',
            data: {
                labels: calorieDates,
                datasets: [{
                    label: 'Calories',
                    data: calorieData,
                    backgroundColor: 'rgba(243, 201, 105, 0.2)',
                    borderColor: 'rgba(243, 201, 105, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Calories (kcal)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Daily Calorie Intake'
                    }
                }
            }
        });
    }
}

/**
 * Initialize activity and workout charts
 */
function initializeActivityCharts() {
    // Weekly workout chart
    const weeklyWorkoutChart = document.getElementById('weeklyWorkoutChart');
    if (weeklyWorkoutChart) {
        // Daily workout data for past 14 days
        const dates = JSON.parse(document.getElementById('workout-dates-data').textContent);
        const durations = JSON.parse(document.getElementById('workout-durations-data').textContent);

        new Chart(weeklyWorkoutChart, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Workout Minutes',
                    data: durations,
                    backgroundColor: 'rgba(161, 178, 212, 0.8)',
                    borderColor: 'rgba(161, 178, 212, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Minutes'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Weekly Workout Minutes'
                    }
                }
            }
        });
    }
}

/**
 * Initialize weight and body metrics charts
 */
function initializeWeightChart() {
    // Weight Chart
    const weightChartCanvas = document.getElementById('weightChart');
    if (weightChartCanvas) {
        const ctx = weightChartCanvas.getContext('2d');
        const metricsDates = JSON.parse(document.getElementById('metrics-dates-data').textContent);
        const weights = JSON.parse(document.getElementById('weights-data').textContent);

        const weightData = {
            labels: metricsDates,
            datasets: [{
                label: 'Weight (kg)',
                data: weights,
                backgroundColor: 'rgba(161, 178, 212, 0.2)',
                borderColor: 'rgba(161, 178, 212, 1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        };

        const weightChart = new Chart(ctx, {
            type: 'line',
            data: weightData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            precision: 1
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.raw + ' kg';
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Weight Trend'
                    }
                }
            }
        });
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupHealthCharts();
});