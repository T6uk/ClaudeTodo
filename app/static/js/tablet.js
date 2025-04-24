// Update time and date
function updateDateTime() {
    const now = new Date();

    // Update time
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    document.getElementById('current-time').textContent = `${hours}:${minutes}`;

    // Update date
    const options = {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    };
    document.getElementById('current-date').textContent = now.toLocaleDateString('et-EE', options);

    // Update every minute (precisely at the start of the next minute)
    const nextMinute = 60000 - (now.getSeconds() * 1000 + now.getMilliseconds());
    setTimeout(updateDateTime, nextMinute);
}

// Fetch weather data from our proxy endpoint
function fetchWeatherData() {
    // Add loading state
    const weatherContainer = document.getElementById('weather-container');
    weatherContainer.classList.add('weather-loading');

    fetch('/api/weather-tartu')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update the weather information in the UI with a nice fade effect
            const tempEl = document.getElementById('header-temp');
            const locEl = document.getElementById('header-loc');
            const iconEl = document.getElementById('header-weather-icon');

            // Apply transition effect
            [tempEl, locEl, iconEl].forEach(el => {
                el.style.opacity = '0';
                setTimeout(() => {
                    if (el === tempEl) el.textContent = data.temp;
                    if (el === locEl) el.textContent = `${data.location}, ${data.condition}`;
                    if (el === iconEl) el.textContent = data.icon;

                    el.style.opacity = '1';
                }, 300);
            });

            // Remove loading state
            setTimeout(() => {
                weatherContainer.classList.remove('weather-loading');
            }, 500);

            console.log('Weather data updated successfully');
        })
        .catch(error => {
            console.error('Error fetching weather data:', error);
            // Set fallback values
            document.getElementById('header-temp').textContent = '22°C';
            document.getElementById('header-loc').textContent = 'Tartu, Päikseline';
            document.getElementById('header-weather-icon').textContent = '☀️';

            // Remove loading state
            weatherContainer.classList.remove('weather-loading');
        });
}

// Auto refresh page every 5 minutes
function setupAutoRefresh() {
    setTimeout(function () {
        window.location.reload();
    }, 5 * 60 * 1000);
}

document.addEventListener('DOMContentLoaded', function () {
    // Initialize time and date
    updateDateTime();

    // Fetch weather data initially
    fetchWeatherData();

    // Then update weather data every 30 minutes
    setInterval(fetchWeatherData, 120 * 60 * 1000);

    // Setup auto-refresh
    setupAutoRefresh();

    // Add staggered animation to items
    const todoItems = document.querySelectorAll('.todo-item');
    const eventItems = document.querySelectorAll('.event-item');

    [...todoItems, ...eventItems].forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';

        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 100 + (index * 50));
    });
});

function getRandomLoveMessage() {
    const messages = [
        {title: "Tere hommikust Musi!💖", message: "Armastan Sind!"},
        {title: "Ilusat päeva Kallis!✨", message: "Iga hetk Sinuga on nagu unistuste täitumine!"},
        {title: "Hommikut, mu kaunis Printsess!👑", message: "Loodan et sul tuleb imeline päev!"},
        {title: "Hommiku kallistus sulle! 💐", message: "Oled imeline!"},
        {title: "Hei kenakene! 💞", message: "Oled imeline!"},
        {title: "Ärka üles, mu südameröövel!💘", message: "Oled minu kõige kallim aare!"},
        {title: "Oi, kesse üles ärkas!🌹", message: "KALLISTAN!!"},
        {title: "Tere hommikust, mu armastus! 🌞", message: "Su naer on mu päikesevalgus!"},
        {title: "Hommik, mu ilus! 🌸", message: "Tänan sind, et oled mu kõrval!"},
        {title: "Tere, mu väike õnn! 🍀", message: "Oled kõige parem asi, mis mulle kunagi juhtunud on!"}
    ];
    return messages[Math.floor(Math.random() * messages.length)];
}

function setupLoveNotification() {
    const now = new Date();
    const estonianTime = new Date(now.toLocaleString("en-US", {timeZone: "Europe/Tallinn"}));
    const currentHour = estonianTime.getHours();
    const currentMinutes = estonianTime.getMinutes();
    const totalMinutes = currentHour * 60 + currentMinutes;

    // TESTING WINDOW: 00:00 (0) to 00:05 (5) Estonian time
    const notificationStart = 7 * 60;    // 7:00 AM (420 minutes)
    const notificationEnd = 9 * 60;     // 9:00 AM (540 minutes)

    // Check if current time is within the testing window
    const shouldShowNotification = totalMinutes >= notificationStart && totalMinutes < notificationEnd;

    // For testing: Uncomment next line to always show notification regardless of time
    // const shouldShowNotification = true;

    const notification = document.getElementById('love-notification');
    if (!notification) return;

    // Setup close button
    const closeButton = notification.querySelector('.love-notification-close');
    if (closeButton) {
        closeButton.addEventListener('click', function () {
            notification.classList.remove('show');
            localStorage.setItem('notificationClosed', 'true');
        });
    }

    if (shouldShowNotification && localStorage.getItem('notificationClosed') !== 'true') {
        // Get random message
        const loveMsg = getRandomLoveMessage();
        const titleEl = notification.querySelector('.love-notification-text h3');
        const messageEl = notification.querySelector('.love-notification-text p');

        if (titleEl && messageEl) {
            titleEl.textContent = loveMsg.title;
            messageEl.textContent = loveMsg.message;
        }

        // Show notification
        notification.classList.add('show');

        // Calculate how many minutes left until 00:05
        const minutesLeft = notificationEnd - totalMinutes;
        const hideTimeout = minutesLeft * 60 * 1000; // Convert to milliseconds

        // Auto-hide at 00:05
        setTimeout(() => {
            notification.classList.remove('show');
            localStorage.removeItem('notificationClosed');
        }, hideTimeout);
    } else {
        localStorage.removeItem('notificationClosed');
    }
}

// Run on page load and check every minute
document.addEventListener('DOMContentLoaded', function () {
    setupLoveNotification();
    setInterval(setupLoveNotification, 60000); // Check every minute
});