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

// Calculate Easter date for a given year
function calculateEaster(year) {
    // This is an implementation of the Meeus/Jones/Butcher algorithm
    const a = year % 19;
    const b = Math.floor(year / 100);
    const c = year % 100;
    const d = Math.floor(b / 4);
    const e = b % 4;
    const f = Math.floor((b + 8) / 25);
    const g = Math.floor((b - f + 1) / 3);
    const h = (19 * a + b - d - g + 15) % 30;
    const i = Math.floor(c / 4);
    const k = c % 4;
    const l = (32 + 2 * e + 2 * i - h - k) % 7;
    const m = Math.floor((a + 11 * h + 22 * l) / 451);
    const month = Math.floor((h + l - 7 * m + 114) / 31);
    const day = ((h + l - 7 * m + 114) % 31) + 1;

    return new Date(year, month - 1, day);
}

// Check if today is a special holiday
function checkForHoliday() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1; // JavaScript months are 0-indexed
    const day = now.getDate();
    const dayOfWeek = now.getDay(); // 0 = Sunday, 1 = Monday, etc.

    // Format as MM-DD for easy comparison
    const dateKey = `${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

    // Define holidays with their messages
    const holidays = {
        // Estonian holidays - fixed dates
        "02-24": {
            title: "Head Vabariigi aastapäeva Kallis! 🇪🇪",
            message: "Elagu Eesti!"
        },
        "05-01": {
            title: "Head Kevadpüha Kallis! 🌱",
            message: "Naudime koos kevade saabumist!"
        },
        "06-14": {
            title: "Head Leinapäeva Kallis! 🕯️",
            message: "Mõtleme koos meie eelkäijatele."
        },
        "06-23": {
            title: "Head Võidupüha Kallis! 🎉",
            message: "Armastan Sind nii väga!"
        },
        "06-24": {
            title: "Ilusat Jaanipäeva Kallis! 🔥",
            message: "Meie armastus põleb tugevamalt kui jaanilõke!"
        },
        "08-20": {
            title: "Head Taasiseseisvumispäeva! 🇪🇪",
            message: "Kallis, oled mu südames!"
        },
        "09-01": {
            title: "Ilusat Teadmistepäeva Kallis! 📚",
            message: "Iga päev Sinuga õpin midagi uut!"
        },
        "11-02": {
            title: "Rahulikku Hingedepäeva Kallis! 🕯️",
            message: "Hoian Sind oma südames alati!"
        },
        "12-24": {
            title: "Häid Jõule mu Kullake! 🎄",
            message: "Armastan Sind jõuluõhtul ja igal teisel õhtul!"
        },
        "12-25": {
            title: "Häid Jõule mu Päkapikuke! 🎄",
            message: "Oled mu kõige ilusam kingitus!"
        },
        "12-26": {
            title: "Häid Jõulupühi Kallis! 🎁",
            message: "Jõulusoojust ja armastust!"
        },

        // Worldwide holidays - fixed dates
        "01-01": {
            title: "Head Uut Aastat Kallis! 🎊",
            message: "Uus aasta täis armastust Sinuga!"
        },
        "02-14": {
            title: "Head Sõbrapäeva mu Armastus! ❤️",
            message: "Oled mu igavene valentiin!"
        },
        "03-08": {
            title: "Ilusat Naistepäeva Kallis! 💐",
            message: "Armastan Sind nii väga!"
        },
        "05-09": {
            title: "Head Euroopa Päeva Kallis! 🇪🇺",
            message: "Maailma parim eurooplane on mu kõrval!"
        },
        "06-01": {
            title: "Head Lastekaitsepäeva Kallis! 👶",
            message: "Sa muudad mind paremaks inimeseks iga päev!"
        },
        "10-01": {
            title: "Head Muusikapäeva Kallis! 🎵",
            message: "Sinu naer on mu lemmikmuusika!"
        },
        "10-31": {
            title: "Happy Halloween Kallis! 🎃",
            message: "Sa oled mu magus komm!"
        },
        "11-19": {
            title: "Head Meestepäeva Kallis! 🥂",
            message: "ARMASTAN ARMASTAN ARMASTAN!"
        },
        "12-31": {
            title: "Head Vana-aasta õhtut Kallis! 🥂",
            message: "Uus aasta täis armastust on meie ees!"
        }
    };

    // Check for holidays with variable dates

    // Calculate Easter for current year
    const easterDate = calculateEaster(year);
    const easterMonth = easterDate.getMonth() + 1;
    const easterDay = easterDate.getDate();

    // Check if today is Easter
    if (month === easterMonth && day === easterDay) {
        return {
            title: "Häid Lihavõtteid Kallis! 🐣",
            message: "Palju värvitud mune ja armastust!"
        };
    }

    // Good Friday (3 days before Easter)
    const goodFriday = new Date(easterDate);
    goodFriday.setDate(easterDate.getDate() - 2);
    if (month === goodFriday.getMonth() + 1 && day === goodFriday.getDate()) {
        return {
            title: "Head Suurt Reedet Kallis! 🙏",
            message: "Rahulikku püha Sinuga!"
        };
    }

    // Shrove Tuesday (47 days before Easter)
    const shroveTuesday = new Date(easterDate);
    shroveTuesday.setDate(easterDate.getDate() - 47);
    if (month === shroveTuesday.getMonth() + 1 && day === shroveTuesday.getDate()) {
        return {
            title: "Head Vastlapäeva Kallis! 🛷",
            message: "Head liugu ja maitsvaid vastlakukleid!"
        };
    }

    // Mother's Day - Second Sunday in May
    if (month === 5 && dayOfWeek === 0) {
        // Check if it's the second Sunday
        const firstDayOfMay = new Date(now.getFullYear(), 4, 1);
        const dayOfWeekOfFirst = firstDayOfMay.getDay();
        const daysUntilFirstSunday = dayOfWeekOfFirst === 0 ? 0 : 7 - dayOfWeekOfFirst;
        const secondSunday = 1 + daysUntilFirstSunday + 7;

        if (day === secondSunday) {
            return {
                title: "Ilusat Emadepäeva mu Kallis! 🌸",
                message: "Oled maailma parim!"
            };
        }
    }

    // Father's Day in Estonia - Second Sunday in November
    if (month === 11 && dayOfWeek === 0) {
        // Check if it's the second Sunday
        const firstDayOfNov = new Date(now.getFullYear(), 10, 1);
        const dayOfWeekOfFirst = firstDayOfNov.getDay();
        const daysUntilFirstSunday = dayOfWeekOfFirst === 0 ? 0 : 7 - dayOfWeekOfFirst;
        const secondSunday = 1 + daysUntilFirstSunday + 7;

        if (day === secondSunday) {
            return {
                title: "Ilusat Isadepäeva mu Kallis! 👨‍👧",
                message: "Oled parim!"
            };
        }
    }

    // First Advent - Fourth Sunday before Christmas
    const christmas = new Date(year, 11, 25);
    const christmasDayOfWeek = christmas.getDay();
    const daysToSubtract = christmasDayOfWeek + 21; // 3 Sundays + days until Christmas Sunday
    const firstAdvent = new Date(year, 11, 25 - daysToSubtract);

    if (month === firstAdvent.getMonth() + 1 && day === firstAdvent.getDate()) {
        return {
            title: "Õnnelikku Esimest Adventi Kallis! 🕯️",
            message: "Jõuluootus koos Sinuga on kõige magusam!"
        };
    }

    // Check for defined date-based holidays
    if (holidays[dateKey]) {
        return holidays[dateKey];
    }

    // No holiday today
    return null;
}

// Track which love messages have been shown, to ensure no repeats
function getNextLoveMessage() {
    // First check if today is a special holiday
    const holidayMessage = checkForHoliday();
    if (holidayMessage) {
        return holidayMessage;
    }

    const messages = [
        // Estonian messages
        {title: "Tere hommikust Musi!💖", message: "Armastan Sind!"},
        {title: "Ilusat päeva Kallis!✨", message: "Iga hetk Sinuga on nagu unistuste täitumine!"},
        {title: "Hommikut, mu kaunis Printsess!👑", message: "Loodan et sul tuleb imeline päev!"},
        {title: "Hommiku kallistus Sulle! 💐", message: "Oled imeline!"},
        {title: "Hei kenakene! 💞", message: "Musid-Kallid-Õhupallid!"},
        {title: "Ärka üles, mu südameröövel!💘", message: "Oled minu kõige kallim aare!"},
        {title: "Oi, kesse üles ärkas!🌹", message: "KALLISTAN!!"},
        {title: "Tere hommikust, mu Armastus! 🌞", message: "Su naer on kui päikesevalgus!"},
        {title: "Hommik, mu ilus Neiu! 🌸", message: "Tänan sind, et oled mu kõrval!"},
        {title: "Meow Meow Kullakene! 😻😻", message: "MUSI OLED!!"},
        {title: "Heyy, mu väike Kullapai! 🍀", message: "Oled kõige parem asi, mis muinuga kunagi juhtunud on!"},

        // Spanish messages
        {title: "Buenos días, mi amor! 💗", message: "Te quiero con todo mi corazón!"},
        {title: "Hola preciosa! ✨", message: "Cada día contigo es una bendición!"},
        {title: "Despierta, mi bella! 🌞", message: "Eres el sueño del que nunca quiero despertar!"},
        {title: "¡Buen día, mi cielo! 🌈", message: "Eres la luz que ilumina mi vida!"},

        // Italian messages
        {title: "Buongiorno, tesoro mio! 💖", message: "Ti amo più di ogni cosa al mondo!"},
        {title: "Ciao bellissima! 🌹", message: "Sei la gioia della mia vita!"},
        {title: "Svegliati, amore mio! ✨", message: "Sei il battito del mio cuore!"},
        {title: "Buon giorno, mia cara! 🌞", message: "Ogni giorno con te è un dono prezioso!"},

        // French messages
        {title: "Bonjour mon amour! 💝", message: "Je t'aime plus que les mots peuvent dire!"},
        {title: "Salut ma chérie! 🌷", message: "Tu es la plus belle chose dans ma vie!"},
        {title: "Réveille-toi, ma princesse! ✨", message: "Mon cœur t'appartient pour toujours!"},
        {title: "Bonjour ma belle! 🥐", message: "Chaque jour avec toi est comme un rêve!"}
    ];

    // Get today's date in format YYYY-MM-DD as string for consistency
    const today = new Date().toLocaleDateString('en-CA');

    // Check if we already selected a message for today
    let todaysMessageIndex = localStorage.getItem('loveMessageIndex_' + today);

    // If we already have a message for today, use that
    if (todaysMessageIndex !== null) {
        return messages[parseInt(todaysMessageIndex)];
    }

    // If no message selected for today, we need to pick one that hasn't been shown recently
    // Try to get the already shown messages sequence from localStorage
    let shownSequence = [];
    let shownSequenceStr = localStorage.getItem('shownLoveMessageSequence');

    if (shownSequenceStr) {
        try {
            shownSequence = JSON.parse(shownSequenceStr);
            // Validate that each index is a number within our range
            shownSequence = shownSequence.filter(index =>
                typeof index === 'number' && index >= 0 && index < messages.length);
        } catch (e) {
            // Reset if there's an error parsing
            console.error('Error parsing shown message sequence:', e);
            shownSequence = [];
        }
    }

    // Create list of available message indices (ones not recently shown)
    let availableIndices = [];
    for (let i = 0; i < messages.length; i++) {
        if (!shownSequence.includes(i)) {
            availableIndices.push(i);
        }
    }

    // If all messages have been shown, reset sequence
    if (availableIndices.length === 0) {
        console.log('All messages have been shown, shuffling and starting again');
        shownSequence = []; // Reset shown messages

        // All messages are available again
        for (let i = 0; i < messages.length; i++) {
            availableIndices.push(i);
        }

        // Shuffle the available indices (Fisher-Yates shuffle)
        for (let i = availableIndices.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [availableIndices[i], availableIndices[j]] = [availableIndices[j], availableIndices[i]];
        }
    }

    // Pick a random available index
    const randomIndex = Math.floor(Math.random() * availableIndices.length);
    const selectedIndex = availableIndices[randomIndex];

    // Add the selected index to our shown sequence
    shownSequence.push(selectedIndex);

    // Save the updated sequence
    localStorage.setItem('shownLoveMessageSequence', JSON.stringify(shownSequence));

    // Save today's message
    localStorage.setItem('loveMessageIndex_' + today, selectedIndex);

    return messages[selectedIndex];
}

function setupLoveNotification() {
    const now = new Date();
    const estonianTime = new Date(now.toLocaleString("en-US", {timeZone: "Europe/Tallinn"}));
    const currentHour = estonianTime.getHours();
    const currentMinutes = estonianTime.getMinutes();
    const totalMinutes = currentHour * 60 + currentMinutes;

    // Define notification window: 5:00 AM (300 minutes) to 9:00 AM (540 minutes)
    const notificationStart = 5 * 60 + 0;   // 5:00 AM (300 minutes)
    const notificationEnd = 10 * 60 + 0;     // 9:00 AM (540 minutes)

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

        // Get next message in non-repeating sequence
        const loveMsg = getNextLoveMessage();
        const titleEl = notification.querySelector('.love-notification-text h3');
        const messageEl = notification.querySelector('.love-notification-text p');

        if (titleEl && messageEl) {
            titleEl.textContent = loveMsg.title;
            messageEl.textContent = loveMsg.message;
        }

        // Show notification
        notification.classList.add('show');

        // Mark that we've shown notification today
        localStorage.setItem(notificationShownKey, 'true');

        // Calculate how many minutes left until notification window ends
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