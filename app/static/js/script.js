document.addEventListener('DOMContentLoaded', function () {
    // Flash message dismissal with animation
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Add close button
        const closeBtn = document.createElement('span');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.position = 'absolute';
        closeBtn.style.right = '10px';
        closeBtn.style.top = '10px';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.fontSize = '20px';
        closeBtn.addEventListener('click', () => dismissAlert(alert));
        alert.appendChild(closeBtn);

        // Auto-dismiss after delay
        setTimeout(() => dismissAlert(alert), 5000);
    });

    function dismissAlert(alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            alert.style.display = 'none';
        }, 500);
    }

    // Format dates and check for overdue tasks
    formatDatesAndCheckDue();

    // Set minimum date for datetime-local inputs
    setupDateInputs();

    // Priority selection styling
    setupPrioritySelect();

    // Setup theme toggle
    setupThemeToggle();

    // Add custom styling to completed checkbox
    setupCompletedCheckbox();

    // Setup mobile navigation
    setupMobileNav();

    // Add subtle animations
    setupAnimations();

    // Setup expandable descriptions
    setupExpandableDescriptions();

    // Setup mobile-friendly calendar
    setupMobileCalendar();
});

function formatDatesAndCheckDue() {
    const dateElements = document.querySelectorAll('.date-format');
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    dateElements.forEach(element => {
        const date = new Date(element.textContent);

        // Format the date nicely
        const options = {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        element.textContent = date.toLocaleDateString('et-EE', options);

        // Add due date status classes
        if (element.classList.contains('due-date')) {
            const dueDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

            if (dueDate < today) {
                element.classList.add('overdue');
                element.parentElement.insertAdjacentHTML('afterbegin', '<span class="badge priority-high">Hilinenud</span> ');
            } else if (dueDate.getTime() === today.getTime()) {
                element.classList.add('today');
                element.parentElement.insertAdjacentHTML('afterbegin', '<span class="badge priority-medium">Täna</span> ');
            } else {
                element.classList.add('upcoming');
            }
        }
    });
}

function setupDateInputs() {
    const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
    if (dateInputs.length > 0) {
        const now = new Date();
        // Format: YYYY-MM-DDThh:mm
        const formattedDate = now.toISOString().slice(0, 16);

        dateInputs.forEach(input => {
            if (!input.value) {
                input.min = formattedDate;
                input.value = formattedDate;
            }
        });
    }
}

function setupPrioritySelect() {
    const prioritySelect = document.getElementById('priority');
    if (prioritySelect) {
        function updateSelectStyle() {
            prioritySelect.className = 'form-control';
            prioritySelect.classList.add('priority-' + prioritySelect.value);
        }

        prioritySelect.addEventListener('change', updateSelectStyle);
        updateSelectStyle(); // Set initial style
    }
}

function setupThemeToggle() {
    // Add theme toggle button to navbar actions if it doesn't exist
    const navbarActions = document.querySelector('.navbar-actions');
    if (navbarActions && !document.querySelector('.theme-toggle')) {
        const themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle';
        themeToggle.innerHTML = '🌙'; // Moon emoji for initial state
        themeToggle.setAttribute('title', 'Lülita tume/hele režiim');
        themeToggle.setAttribute('aria-label', 'Lülita tume režiim');
        navbarActions.appendChild(themeToggle);

        // Check for saved theme preference
        const darkMode = localStorage.getItem('darkMode') === 'true';
        if (darkMode) {
            document.body.classList.add('dark-mode');
            themeToggle.innerHTML = '☀️'; // Sun emoji for dark mode
        }

        // Add event listener
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
            this.innerHTML = isDarkMode ? '☀️' : '🌙';

            // Add a subtle animation to the entire page when theme changes
            document.body.style.transition = 'background-color 0.5s ease, color 0.5s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 500);
        });

        // Add theme toggle to mobile drawer if it exists
        const mobileDrawerFooter = document.querySelector('.mobile-drawer-footer');
        if (mobileDrawerFooter && !mobileDrawerFooter.querySelector('.theme-toggle')) {
            const mobileThemeToggle = themeToggle.cloneNode(true);
            mobileDrawerFooter.appendChild(mobileThemeToggle);

            // Add event listener to mobile theme toggle
            mobileThemeToggle.addEventListener('click', function() {
                document.body.classList.toggle('dark-mode');
                const isDarkMode = document.body.classList.contains('dark-mode');
                localStorage.setItem('darkMode', isDarkMode);

                // Update all theme toggles
                document.querySelectorAll('.theme-toggle').forEach(toggle => {
                    toggle.innerHTML = isDarkMode ? '☀️' : '🌙';
                });

                // Animation
                document.body.style.transition = 'background-color 0.5s ease, color 0.5s ease';
                setTimeout(() => {
                    document.body.style.transition = '';
                }, 500);
            });
        }
    }
}

function setupCompletedCheckbox() {
    const completedCheckbox = document.getElementById('completed');
    if (completedCheckbox) {
        // Create a visual upgrade for the checkbox
        const checkboxContainer = completedCheckbox.parentElement;
        checkboxContainer.className = 'checkbox';
    }
}

function setupMobileNav() {
    // Setup mobile navigation toggle
    const mobileToggle = document.querySelector('.mobile-nav-toggle');
    const mobileDrawer = document.querySelector('.mobile-drawer');
    const mobileOverlay = document.querySelector('.mobile-drawer-overlay');

    if (mobileToggle && mobileDrawer && mobileOverlay) {
        // Handle mobile toggle click
        mobileToggle.addEventListener('click', function() {
            mobileDrawer.classList.add('active');
            mobileOverlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        });

        // Setup mobile drawer close functionality
        const closeBtn = mobileDrawer.querySelector('.mobile-drawer-close');

        if (closeBtn) {
            closeBtn.addEventListener('click', closeMobileMenu);
        }

        // Close when clicking overlay
        mobileOverlay.addEventListener('click', closeMobileMenu);

        // Close when clicking a link in the drawer
        const drawerLinks = mobileDrawer.querySelectorAll('.nav-link');
        drawerLinks.forEach(link => {
            link.addEventListener('click', closeMobileMenu);
        });

        // Close with escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && mobileDrawer.classList.contains('active')) {
                closeMobileMenu();
            }
        });

        // Animation for menu items
        const menuItems = mobileDrawer.querySelectorAll('.nav-link');
        menuItems.forEach((item, index) => {
            item.style.opacity = "0";
            item.style.transform = "translateX(20px)";

            mobileToggle.addEventListener('click', function() {
                setTimeout(() => {
                    item.style.transition = "opacity 0.3s ease, transform 0.3s ease";
                    item.style.opacity = "1";
                    item.style.transform = "translateX(0)";
                }, 100 + (index * 50)); // Staggered animation
            });
        });
    }

    function closeMobileMenu() {
        mobileDrawer.classList.remove('active');
        mobileOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling

        // Reset menu item animations
        const menuItems = mobileDrawer.querySelectorAll('.nav-link');
        menuItems.forEach(item => {
            item.style.transition = "none";
            item.style.opacity = "0";
            item.style.transform = "translateX(20px)";
        });
    }
}

function setupAnimations() {
    // Subtle hover effects for buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function () {
            this.style.transition = 'all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        });
    });

    // Enhance form inputs with focus animation
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('input-focused');
        });

        input.addEventListener('blur', function () {
            this.parentElement.classList.remove('input-focused');
        });
    });
}

// Setup expandable descriptions for mobile
function setupExpandableDescriptions() {
    const expandables = document.querySelectorAll('.expandable');
    expandables.forEach(elem => {
        elem.addEventListener('click', function() {
            this.classList.toggle('expanded');
        });
    });
}

// Add subtle animations to todo cards
function animateTodoCards() {
    const cards = document.querySelectorAll('.todo-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index); // Stagger the animations
    });
}

// Setup mobile-friendly calendar interactions
function setupMobileCalendar() {
    // Add better touch interactions for week calendar
    const weekCalendar = document.querySelector('.week-calendar-wrapper');
    if (weekCalendar) {
        // Add visual indicator for scrollable area on small screens
        if (window.innerWidth <= 768) {
            const indicator = document.createElement('div');
            indicator.className = 'scroll-indicator';
            indicator.innerHTML = '← Keri →';
            indicator.style.textAlign = 'center';
            indicator.style.fontSize = '0.8rem';
            indicator.style.color = 'var(--gray-500)';
            indicator.style.padding = '5px 0';
            indicator.style.marginBottom = '5px';
            weekCalendar.parentNode.insertBefore(indicator, weekCalendar);

            // Remove the indicator after user has scrolled
            weekCalendar.addEventListener('scroll', function() {
                indicator.style.opacity = '0';
                setTimeout(() => {
                    indicator.remove();
                }, 300);
            }, { once: true });
        }
    }

    // Make calendar cells more touch-friendly
    const calendarCells = document.querySelectorAll('.calendar td');
    calendarCells.forEach(cell => {
        // Make the entire cell clickable to add event
        if (!cell.classList.contains('empty-day')) {
            const addBtn = cell.querySelector('.add-event-btn');
            if (addBtn) {
                const dayDate = addBtn.getAttribute('href');

                // Add touch feedback
                cell.addEventListener('click', function(e) {
                    // Only respond if clicked directly on the cell (not on an event)
                    if (e.target === cell || e.target === cell.querySelector('.day-number') || e.target === cell.querySelector('.events')) {
                        window.location.href = dayDate;
                    }
                });
            }
        }
    });

    // Enhance calendar events for touch
    const calendarEvents = document.querySelectorAll('.calendar-event, .day-event, .week-event');
    calendarEvents.forEach(event => {
        // Add touch feedback
        event.addEventListener('touchstart', function() {
            this.style.opacity = '0.7';
        });

        event.addEventListener('touchend', function() {
            this.style.opacity = '1';
        });
    });
}

// Run animation when page is fully loaded
window.onload = function () {
    animateTodoCards();
};