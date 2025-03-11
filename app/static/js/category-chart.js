/**
 * Challenge categories chart styling
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add colors for category charts
    const categoryColors = {
        'General': '#6c757d',
        'Fitness': '#28a745',
        'Learning': '#17a2b8',
        'Productivity': '#007bff',
        'Finance': '#fd7e14',
        'Health': '#20c997',
        'Social': '#e83e8c',
        'Other': '#6610f2'
    };

    // Style category progress bars
    const categoryBars = document.querySelectorAll('.category-progress');
    categoryBars.forEach(bar => {
        const category = bar.closest('.category-item').querySelector('.category-label span').textContent;
        if (categoryColors[category]) {
            bar.style.backgroundColor = categoryColors[category];
        }
    });

    // Apply tooltips to category items if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const categoryItems = document.querySelectorAll('.badge-category');
        categoryItems.forEach(item => {
            new bootstrap.Tooltip(item);
        });
    }
});