// Main JavaScript for Personal Website

// Wait for document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Update navbar appearance on theme change
    window.addEventListener('themechange', function(e) {
        updateNavbarForTheme(e.detail.theme);
    });

    // Initialize navbar based on current theme
    updateNavbarForTheme(document.documentElement.getAttribute('data-bs-theme'));

    // Log initialization
    console.log('Personal Website initialized');
});

// Update navbar appearance based on theme
function updateNavbarForTheme(theme) {
    const navbar = document.querySelector('.navbar');
    const footer = document.querySelector('footer');

    if (!navbar) return;

    if (theme === 'dark') {
        navbar.classList.remove('navbar-dark', 'bg-dark');
        navbar.classList.add('navbar-dark', 'bg-dark');

        if (footer) {
            footer.classList.remove('bg-light', 'text-dark');
            footer.classList.add('bg-dark', 'text-white');
        }
    } else {
        navbar.classList.remove('navbar-dark', 'bg-dark');
        navbar.classList.add('navbar-dark', 'bg-primary');

        if (footer) {
            footer.classList.remove('bg-dark', 'text-white');
            footer.classList.add('bg-dark', 'text-white');
        }
    }
}