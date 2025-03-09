// theme.js - Handles theme switching functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or use preferred color scheme
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Set initial theme based on saved preference or system preference
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
        if (document.getElementById('themeToggle')) {
            document.getElementById('themeToggle').checked = true;
        }

        // Update the icon to moon
        if (document.getElementById('themeIcon')) {
            document.getElementById('themeIcon').classList.remove('bi-sun');
            document.getElementById('themeIcon').classList.add('bi-moon');
        }
    } else {
        document.documentElement.setAttribute('data-bs-theme', 'light');
        if (document.getElementById('themeToggle')) {
            document.getElementById('themeToggle').checked = false;
        }

        // Update the icon to sun
        if (document.getElementById('themeIcon')) {
            document.getElementById('themeIcon').classList.remove('bi-moon');
            document.getElementById('themeIcon').classList.add('bi-sun');
        }
    }

    // Toggle theme when the switch is clicked
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                // Switch to dark theme
                document.documentElement.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                // Update toggle icon
                document.getElementById('themeIcon').classList.remove('bi-sun');
                document.getElementById('themeIcon').classList.add('bi-moon');
            } else {
                // Switch to light theme
                document.documentElement.setAttribute('data-bs-theme', 'light');
                localStorage.setItem('theme', 'light');
                // Update toggle icon
                document.getElementById('themeIcon').classList.remove('bi-moon');
                document.getElementById('themeIcon').classList.add('bi-sun');
            }
        });
    }
});