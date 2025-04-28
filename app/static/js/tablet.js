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
function fetchWeather() {
    fetch('/api/weather-tartu')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('header-temp').textContent = data.temp;
                document.getElementById('header-loc').textContent = data.condition;
                document.getElementById('header-weather-icon').textContent = data.icon;
            } else {
                console.error('Weather fetch failed:', data.error);
                // Use fallback values if API fails
                document.getElementById('header-temp').textContent = '---';
                document.getElementById('header-loc').textContent = 'Tartu';
                document.getElementById('header-weather-icon').textContent = '👻';
            }
        })
        .catch(error => {
            console.error('Weather fetch error:', error);
            // Use fallback values if fetch fails completely
            document.getElementById('header-temp').textContent = '---';
            document.getElementById('header-loc').textContent = 'Tartu';
            document.getElementById('header-weather-icon').textContent = '👻';
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
        {title: "Hei kenakene! 💞", message: "Musid-Kallid-Õhupallid!"},
        {title: "Ärka üles, mu südameröövel!💘", message: "Oled minu kõige kallim aare!"},
        {title: "Oi, kesse üles ärkas!🌹", message: "KALLISTAN!!"},
        {title: "Tere hommikust, mu armastus! 🌞", message: "Su naer on mu päikesevalgus!"},
        {title: "Hommik, mu ilus! 🌸", message: "Tänan sind, et oled mu kõrval!"},
        {title: "Meow Meow Kullakene! 😻😻", message: "MUSI OLED!!"},
        {title: "Tere, mu väike õnn! 🍀", message: "Oled kõige parem asi, mis muinuga kunagi juhtunud on!"}
    ];

    // Get today's date in format YYYY-MM-DD as string
    const today = new Date().toLocaleDateString('en-CA'); // Use Canadian locale for YYYY-MM-DD format

    // Check if we already selected a message for today
    let todaysMessageIndex = localStorage.getItem('loveMessageIndex_' + today);

    // If no message selected for today, pick a random one and save it
    if (todaysMessageIndex === null) {
        todaysMessageIndex = Math.floor(Math.random() * messages.length);
        localStorage.setItem('loveMessageIndex_' + today, todaysMessageIndex);
    } else {
        // Convert from string to number
        todaysMessageIndex = parseInt(todaysMessageIndex);
    }

    return messages[todaysMessageIndex];
}

function setupLoveNotification() {
    const now = new Date();
    const estonianTime = new Date(now.toLocaleString("en-US", {timeZone: "Europe/Tallinn"}));
    const currentHour = estonianTime.getHours();
    const currentMinutes = estonianTime.getMinutes();
    const totalMinutes = currentHour * 60 + currentMinutes;

    // Define notification window: 20:25 (1225 minutes) to 20:30 (1230 minutes)
    const notificationStart = 5 * 60 + 0;   // 5:00 AM (300 minutes)
    const notificationEnd = 9 * 60 + 0;     // 9:00 AM (540 minutes)

    // Check if current time is within the notification window
    const shouldShowNotification = totalMinutes >= notificationStart && totalMinutes < notificationEnd;

    // For testing: Uncomment next line to always show notification regardless of time
    // const shouldShowNotification = true;

    const notification = document.getElementById('love-notification');
    if (!notification) return;

    // Setup close button
    const closeButton = notification.querySelector('.love-notification-close');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            notification.classList.remove('show');
            localStorage.setItem('notificationClosed', 'true');
        });
    }

    // Get today's date as string for storage key
    const today = new Date().toLocaleDateString('en-CA');
    const notificationShownKey = 'notificationShown_' + today;

    // Check if notification shown today and if we're in the time window
    if (shouldShowNotification && localStorage.getItem(notificationShownKey) !== 'true' &&
        localStorage.getItem('notificationClosed') !== 'true') {

        // Get random message for today
        const loveMsg = getRandomLoveMessage();
        const titleEl = notification.querySelector('.love-notification-text h3');
        const messageEl = notification.querySelector('.love-notification-text p');

        if (titleEl && messageEl) {
            titleEl.textContent = loveMsg.title;
            messageEl.textContent = loveMsg.message;
        }

        // Show notification
        notification.classList.add('show');

        // Mark that we've shown notification today
        localStorage.setItem(notificationShownKey, 'false');

        // Calculate how many minutes left until 20:30
        const minutesLeft = notificationEnd - totalMinutes;
        const hideTimeout = minutesLeft * 60 * 1000; // Convert to milliseconds

        // Auto-hide at the end of time window
        setTimeout(() => {
            notification.classList.remove('show');
            localStorage.removeItem('notificationClosed');
        }, hideTimeout);
    } else if (totalMinutes >= notificationEnd) {
        // Reset closed state after the time window
        localStorage.removeItem('notificationClosed');
    }
}

// Run on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initial updates
    updateDateTime();
    setupLoveNotification();
    fetchWeather(); // Initial fetch

    // Update time every second
    setInterval(updateDateTime, 1000);

    // Check notification every minute
    setInterval(setupLoveNotification, 60000);

    // Refresh weather every 30 minutes (1800000 ms)
    // Using 30min to stay well under the API limits
    setInterval(fetchWeather, 1800000);
});
