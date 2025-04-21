document.addEventListener('DOMContentLoaded', function() {
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
        element.textContent = date.toLocaleDateString(undefined, options);

        // Add due date status classes
        if (element.classList.contains('due-date')) {
            const dueDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

            if (dueDate < today) {
                element.classList.add('overdue');
                element.parentElement.insertAdjacentHTML('beforeend', ' <span class="badge priority-high">Overdue</span>');
            } else if (dueDate.getTime() === today.getTime()) {
                element.classList.add('today');
                element.parentElement.insertAdjacentHTML('beforeend', ' <span class="badge priority-medium">Today</span>');
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
    // Add theme toggle button to navbar if it doesn't exist
    const navbar = document.querySelector('.navbar');
    if (navbar && !document.querySelector('.theme-toggle')) {
        const themeToggle = document.createElement('button');
        themeToggle.className = 'theme-toggle';
        themeToggle.innerHTML = '🌙'; // Moon emoji for initial state
        themeToggle.setAttribute('title', 'Toggle dark/light mode');
        navbar.appendChild(themeToggle);

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
        });
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

// Add subtle animations to todo cards
function animateTodoCards() {
    const cards = document.querySelectorAll('.todo-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index); // Stagger the animations
    });
}

// Run animation when page is fully loaded
window.onload = function() {
    animateTodoCards();
};