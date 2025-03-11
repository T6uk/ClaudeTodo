/**
 * Enhanced Theme management for light/dark mode with smooth transitions
 */
(function() {
    // Theme constants
    const THEME_KEY = 'personalWebsiteTheme';
    const DARK_THEME = 'dark';
    const LIGHT_THEME = 'light';

    // DOM elements
    let themeToggleBtns;

    // Initialize theme
    function initTheme() {
        // Get saved theme from localStorage or use system preference as default
        const savedTheme = localStorage.getItem(THEME_KEY);
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        const defaultTheme = savedTheme || (systemPrefersDark ? DARK_THEME : LIGHT_THEME);

        // Add transition class to html for first load (prevents flash)
        document.documentElement.classList.add('theme-transition');

        // Set initial theme without transition
        setTheme(defaultTheme, false);

        // Remove transition prevention class after a short delay
        setTimeout(() => {
            document.documentElement.classList.remove('theme-transition');
        }, 300);

        // Initialize theme toggle buttons
        themeToggleBtns = document.querySelectorAll('.theme-toggle');
        themeToggleBtns.forEach(btn => {
            // Set initial button state
            updateToggleUI(btn, getCurrentTheme());

            // Add click event listener with animation
            btn.addEventListener('click', function() {
                // Add the rotation animation class
                this.classList.add('rotate-animation');

                // Remove the class after animation completes
                setTimeout(() => {
                    this.classList.remove('rotate-animation');
                }, 500);

                toggleTheme();
            });
        });

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
            if (!localStorage.getItem(THEME_KEY)) {
                setTheme(event.matches ? DARK_THEME : LIGHT_THEME);
            }
        });

        // Add CSS for theme toggle animation
        const style = document.createElement('style');
        style.textContent = `
            .rotate-animation {
                animation: theme-toggle-rotate 0.5s ease;
            }
            @keyframes theme-toggle-rotate {
                0% { transform: rotate(0); }
                100% { transform: rotate(360deg); }
            }
            .theme-transition * {
                transition: none !important;
            }
        `;
        document.head.append(style);
    }

    // Get current theme
    function getCurrentTheme() {
        return document.documentElement.getAttribute('data-bs-theme') || LIGHT_THEME;
    }

    // Set theme
    function setTheme(theme, animate = true) {
        // If animate is false, temporarily disable transitions
        if (!animate) {
            document.documentElement.classList.add('theme-transition');
        }

        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem(THEME_KEY, theme);

        // Update all toggle buttons
        if (themeToggleBtns) {
            themeToggleBtns.forEach(btn => updateToggleUI(btn, theme));
        }

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));

        // Update auth page theme if applicable
        updateAuthPageTheme(theme);

        // Re-enable transitions after a short delay if they were disabled
        if (!animate) {
            setTimeout(() => {
                document.documentElement.classList.remove('theme-transition');
            }, 50);
        }
    }

    // Toggle between light and dark themes
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === DARK_THEME ? LIGHT_THEME : DARK_THEME;
        setTheme(newTheme);
    }

    // Update toggle button UI based on current theme
    function updateToggleUI(toggleBtn, theme) {
        const sunIcon = toggleBtn.querySelector('.theme-icon-light');
        const moonIcon = toggleBtn.querySelector('.theme-icon-dark');

        if (theme === DARK_THEME) {
            toggleBtn.setAttribute('aria-label', 'Switch to light mode');
            toggleBtn.title = 'Switch to light mode';
            if (sunIcon) sunIcon.classList.add('d-none');
            if (moonIcon) moonIcon.classList.remove('d-none');
        } else {
            toggleBtn.setAttribute('aria-label', 'Switch to dark mode');
            toggleBtn.title = 'Switch to dark mode';
            if (sunIcon) sunIcon.classList.remove('d-none');
            if (moonIcon) moonIcon.classList.add('d-none');
        }
    }

    // Special handling for auth pages
    function updateAuthPageTheme(theme) {
        const authBody = document.querySelector('.auth-body');
        if (authBody) {
            if (theme === DARK_THEME) {
                authBody.classList.add('auth-body-dark');
                authBody.classList.remove('auth-body-light');
            } else {
                authBody.classList.add('auth-body-light');
                authBody.classList.remove('auth-body-dark');
            }
        }

        // Add page animation
        animatePageContent();
    }

    // Add subtle animation to page content on theme change
    function animatePageContent() {
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.classList.add('theme-content-fade');
            setTimeout(() => {
                mainContent.classList.remove('theme-content-fade');
            }, 500);
        }
    }

    // Add CSS for content animation
    const styleSheet = document.createElement('style');
    styleSheet.textContent = `
        .theme-content-fade {
            animation: theme-content-fade 0.5s ease;
        }
        @keyframes theme-content-fade {
            0% { opacity: 0.8; }
            100% { opacity: 1; }
        }
    `;
    document.head.append(styleSheet);

    // Initialize on DOM content loaded
    document.addEventListener('DOMContentLoaded', initTheme);

    // Expose theme functions to global scope
    window.themeManager = {
        toggle: toggleTheme,
        set: setTheme,
        get: getCurrentTheme
    };
})();