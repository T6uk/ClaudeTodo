// Enhanced theme.js - Handles theme switching functionality with smooth transitions
document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle element
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

    // Check for saved theme preference, system preference, or time-based default
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Time-based theme (dark during evening/night)
    const currentHour = new Date().getHours();
    const isNightTime = currentHour < 6 || currentHour >= 19; // Between 7PM and 6AM

    // Set initial theme based on priority: saved preference > system preference > time-based
    let initialTheme;
    if (savedTheme) {
        initialTheme = savedTheme;
    } else if (prefersDark) {
        initialTheme = 'dark';
    } else if (isNightTime) {
        initialTheme = 'dark';
    } else {
        initialTheme = 'light';
    }

    // Apply the initial theme
    applyTheme(initialTheme);

    // Toggle theme when the switch is clicked
    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            const newTheme = this.checked ? 'dark' : 'light';
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);

            // Add animation to the body to show transition
            document.body.classList.add('theme-transition');
            setTimeout(() => {
                document.body.classList.remove('theme-transition');
            }, 1000);
        });
    }

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        // Only change theme automatically if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
            const newTheme = event.matches ? 'dark' : 'light';
            applyTheme(newTheme);
        }
    });

    // Function to apply theme
    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            if (themeToggle) themeToggle.checked = true;
            if (themeIcon) {
                themeIcon.classList.remove('bi-sun');
                themeIcon.classList.add('bi-moon');
            }

            // Apply dark mode class for components that might need it
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            if (themeToggle) themeToggle.checked = false;
            if (themeIcon) {
                themeIcon.classList.remove('bi-moon');
                themeIcon.classList.add('bi-sun');
            }

            // Apply light mode class for components that might need it
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');
        }

        // Custom event that other scripts can listen for
        document.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: theme }
        }));
    }

    // Add additional theme-related functionality

    // Update chart colors when theme changes
    document.addEventListener('themeChanged', function(e) {
        const isDark = e.detail.theme === 'dark';

        // If any charts exist, update their themes
        if (typeof Chart !== 'undefined') {
            Chart.helpers.each(Chart.instances, function(chart) {
                // Update chart colors based on theme
                updateChartColors(chart, isDark);
                chart.update();
            });
        }
    });

    // Function to update chart colors
    function updateChartColors(chart, isDark) {
        if (!chart.config || !chart.config.data) return;

        const darkPalette = {
            backgroundColor: ['rgba(78, 115, 223, 0.2)', 'rgba(28, 200, 138, 0.2)', 'rgba(54, 185, 204, 0.2)',
                             'rgba(246, 194, 62, 0.2)', 'rgba(231, 74, 59, 0.2)'],
            borderColor: ['rgba(78, 115, 223, 1)', 'rgba(28, 200, 138, 1)', 'rgba(54, 185, 204, 1)',
                         'rgba(246, 194, 62, 1)', 'rgba(231, 74, 59, 1)']
        };

        const lightPalette = {
            backgroundColor: ['rgba(78, 115, 223, 0.2)', 'rgba(28, 200, 138, 0.2)', 'rgba(54, 185, 204, 0.2)',
                              'rgba(246, 194, 62, 0.2)', 'rgba(231, 74, 59, 0.2)'],
            borderColor: ['rgba(78, 115, 223, 1)', 'rgba(28, 200, 138, 1)', 'rgba(54, 185, 204, 1)',
                          'rgba(246, 194, 62, 1)', 'rgba(231, 74, 59, 1)']
        };

        const palette = isDark ? darkPalette : lightPalette;

        // Apply to datasets
        if (chart.config.data.datasets) {
            chart.config.data.datasets.forEach((dataset, i) => {
                // Only update if not explicitly set by the chart
                if (!dataset._backgroundColor) {
                    dataset.backgroundColor = palette.backgroundColor[i % palette.backgroundColor.length];
                }
                if (!dataset._borderColor) {
                    dataset.borderColor = palette.borderColor[i % palette.borderColor.length];
                }
            });
        }

        // Update grid lines
        if (chart.config.options && chart.config.options.scales) {
            const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
            const textColor = isDark ? '#e0e0e0' : '#666';

            Object.values(chart.config.options.scales).forEach(scale => {
                if (scale.grid) scale.grid.color = gridColor;
                if (scale.ticks) scale.ticks.color = textColor;
            });
        }
    }

    // Add CSS for the theme transition
    const style = document.createElement('style');
    style.innerHTML = `
        .theme-transition {
            transition: background-color 0.7s ease, color 0.7s ease !important;
        }
        .theme-transition * {
            transition: background-color 0.7s ease, color 0.7s ease, border-color 0.7s ease !important;
        }
    `;
    document.head.appendChild(style);
});