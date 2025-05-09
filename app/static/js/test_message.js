// Test mode for love messages - accessible via a gesture
let testModeActive = true;
let testPanel = null;

function createTestPanel() {
    // Create test panel if it doesn't exist
    if (!testPanel) {
        testPanel = document.createElement('div');
        testPanel.className = 'message-test-panel';
        testPanel.innerHTML = `
            <div class="test-panel-header">
                <h3>💌 Love Message Test Panel</h3>
                <button id="close-test-panel">×</button>
            </div>
            <div class="test-panel-content">
                <div class="test-section">
                    <h4>Regular Message Testing</h4>
                    <button id="show-next-message">Show Next Message</button>
                    <button id="reset-message-history">Reset Message History</button>
                    <button id="complete-message-cycle">Complete Cycle & Shuffle</button>
                </div>
                <div class="test-section">
                    <h4>Holiday Message Testing</h4>
                    <select id="holiday-selector">
                        <option value="">Select a holiday to test...</option>
                        <option value="01-01">New Year's Day</option>
                        <option value="02-14">Valentine's Day</option>
                        <option value="02-24">Estonian Independence Day</option>
                        <option value="03-08">International Women's Day</option>
                        <option value="easter">Easter</option>
                        <option value="05-01">Spring Day</option>
                        <option value="05-09">Europe Day</option>
                        <option value="mothers-day">Mother's Day</option>
                        <option value="06-01">Children's Day</option>
                        <option value="06-14">Day of Mourning</option>
                        <option value="06-23">Victory Day</option>
                        <option value="06-24">Midsummer Day</option>
                        <option value="08-20">Restoration of Independence Day</option>
                        <option value="09-01">Knowledge Day</option>
                        <option value="10-01">Music Day</option>
                        <option value="10-31">Halloween</option>
                        <option value="11-02">All Souls' Day</option>
                        <option value="11-19">Men's Day</option>
                        <option value="fathers-day">Father's Day</option>
                        <option value="first-advent">First Advent</option>
                        <option value="12-24">Christmas Eve</option>
                        <option value="12-25">Christmas Day</option>
                        <option value="12-26">Boxing Day</option>
                        <option value="12-31">New Year's Eve</option>
                    </select>
                    <button id="test-holiday-message">Test Holiday Message</button>
                </div>
                <div class="test-section">
                    <h4>Time Window Testing</h4>
                    <button id="force-show-notification">Show Notification Now</button>
                    <button id="hide-notification">Hide Notification</button>
                </div>
                <div class="test-status">
                    <p id="test-message-status"></p>
                </div>
            </div>
        `;

        // Apply styles to the test panel
        document.head.insertAdjacentHTML('beforeend', `
            <style>
                .message-test-panel {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.2);
                    width: 350px;
                    z-index: 9999;
                    font-family: 'Inter', sans-serif;
                    display: none;
                    overflow: hidden;
                }
                .test-panel-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px 15px;
                    background: #6366f1;
                    color: white;
                }
                .test-panel-header h3 {
                    margin: 0;
                    font-size: 16px;
                }
                .test-panel-header button {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                }
                .test-panel-content {
                    padding: 15px;
                    max-height: 500px;
                    overflow-y: auto;
                }
                .test-section {
                    margin-bottom: 15px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid #eee;
                }
                .test-section h4 {
                    margin: 0 0 10px 0;
                    font-size: 14px;
                    color: #444;
                }
                .test-section button, .test-section select {
                    padding: 8px 12px;
                    margin: 5px 5px 5px 0;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background: #f5f5f5;
                    cursor: pointer;
                    font-size: 13px;
                }
                .test-section button:hover {
                    background: #e0e0e0;
                }
                .test-section select {
                    width: 100%;
                    box-sizing: border-box;
                }
                .test-status {
                    font-size: 13px;
                    color: #666;
                    background: #f9f9f9;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                #test-message-status {
                    margin: 0;
                }
                #force-show-notification {
                    background: #4caf50;
                    color: white;
                    border-color: #388e3c;
                }
                #hide-notification {
                    background: #f44336;
                    color: white;
                    border-color: #d32f2f;
                }
            </style>
        `);

        document.body.appendChild(testPanel);

        // Set up event handlers
        document.getElementById('close-test-panel').addEventListener('click', toggleTestPanel);
        document.getElementById('show-next-message').addEventListener('click', testNextMessage);
        document.getElementById('reset-message-history').addEventListener('click', resetMessageHistory);
        document.getElementById('complete-message-cycle').addEventListener('click', completeMessageCycle);
        document.getElementById('test-holiday-message').addEventListener('click', testHolidayMessage);
        document.getElementById('force-show-notification').addEventListener('click', forceShowNotification);
        document.getElementById('hide-notification').addEventListener('click', forceHideNotification);
    }

    return testPanel;
}

function toggleTestPanel() {
    if (!testPanel) {
        createTestPanel();
    }

    testModeActive = !testModeActive;
    testPanel.style.display = testModeActive ? 'block' : 'none';
}

// Function to manually show next message in sequence
function testNextMessage() {
    // Get today's date
    const today = new Date().toLocaleDateString('en-CA');

    // Remove today's message selection to force picking a new one
    localStorage.removeItem('loveMessageIndex_' + today);

    // Get and display the next message
    const message = getNextLoveMessage();
    updateTestStatus(`Showing message: "${message.title}" - "${message.message}"`);

    // Show the notification with this message
    showTestMessage(message);
}

// Reset message history to start a fresh cycle
function resetMessageHistory() {
    localStorage.removeItem('shownLoveMessageSequence');
    const today = new Date().toLocaleDateString('en-CA');
    localStorage.removeItem('loveMessageIndex_' + today);

    updateTestStatus('Message history reset. Ready for a new cycle.');
}

// Simulate completing an entire message cycle to test shuffling
function completeMessageCycle() {
    // Get all messages
    const messages = getAllMessages();

    // Create a sequence that includes all messages
    let sequence = [];
    for (let i = 0; i < messages.length; i++) {
        sequence.push(i);
    }

    // Save the sequence as if all messages were shown
    localStorage.setItem('shownLoveMessageSequence', JSON.stringify(sequence));

    // Remove today's message to force a new selection
    const today = new Date().toLocaleDateString('en-CA');
    localStorage.removeItem('loveMessageIndex_' + today);

    // Get the next message (should be from a new shuffled sequence)
    const message = getNextLoveMessage();

    updateTestStatus(`Cycle completed and shuffled. Next message: "${message.title}"`);
    showTestMessage(message);
}

// Test a specific holiday message
function testHolidayMessage() {
    const selector = document.getElementById('holiday-selector');
    const holidayKey = selector.value;

    if (!holidayKey) {
        updateTestStatus('Please select a holiday to test');
        return;
    }

    let holidayMessage;

    // Handle special variable-date holidays
    if (holidayKey === 'easter') {
        holidayMessage = {
            title: "Häid Lihavõtteid Kallis! 🐣",
            message: "Palju värvitud mune ja armastust!"
        };
    } else if (holidayKey === 'mothers-day') {
        holidayMessage = {
            title: "Ilusat Emadepäeva mu Kallis! 🌸",
            message: "Oled maailma parim!"
        };
    } else if (holidayKey === 'fathers-day') {
        holidayMessage = {
            title: "Ilusat Isadepäeva mu Kallis! 👨‍👧",
            message: "Oled parim!"
        };
    } else if (holidayKey === 'first-advent') {
        holidayMessage = {
            title: "Õnnelikku Esimest Adventi Kallis! 🕯️",
            message: "Jõuluootus koos Sinuga on kõige magusam!"
        };
    } else {
        // Get the message for fixed-date holidays
        const holidays = getAllHolidays();
        holidayMessage = holidays[holidayKey];
    }

    if (holidayMessage) {
        updateTestStatus(`Testing holiday message for: ${holidayKey}`);
        showTestMessage(holidayMessage);
    } else {
        updateTestStatus('Could not find message for selected holiday');
    }
}

// Force show the notification regardless of time
function forceShowNotification() {
    const notification = document.getElementById('love-notification');
    if (!notification) {
        updateTestStatus('Notification element not found');
        return;
    }

    const message = getNextLoveMessage();
    const titleEl = notification.querySelector('.love-notification-text h3');
    const messageEl = notification.querySelector('.love-notification-text p');

    if (titleEl && messageEl) {
        titleEl.textContent = message.title;
        messageEl.textContent = message.message;
    }

    showNotification(notification);
    updateTestStatus('Notification shown');
}

// Force hide the notification
function forceHideNotification() {
    const notification = document.getElementById('love-notification');
    if (!notification) {
        updateTestStatus('Notification element not found');
        return;
    }

    hideNotification(notification);
    updateTestStatus('Notification hidden');
}

// Helper function to show a test message
function showTestMessage(message) {
    const notification = document.getElementById('love-notification');
    if (!notification) {
        updateTestStatus('Notification element not found');
        return;
    }

    const titleEl = notification.querySelector('.love-notification-text h3');
    const messageEl = notification.querySelector('.love-notification-text p');

    if (titleEl && messageEl) {
        titleEl.textContent = message.title;
        messageEl.textContent = message.message;
    }

    showNotification(notification);
}

// Update the status display in the test panel
function updateTestStatus(message) {
    const statusElement = document.getElementById('test-message-status');
    if (statusElement) {
        statusElement.textContent = message;
    }
}

// Helper function to get all messages (for testing)
function getAllMessages() {
    return [
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
}

// Helper function to get all holidays (for testing)
function getAllHolidays() {
    return {
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
}

// Add a secret gesture to show the test panel
document.addEventListener('DOMContentLoaded', function() {
    // Add the existing code first

    // Add the secret gesture (triple click on the logo)
    const logoElement = document.querySelector('.logo-icon');
    if (logoElement) {
        let clickCount = 0;
        let clickTimer = null;

        logoElement.addEventListener('click', function() {
            clickCount++;

            if (clickCount === 1) {
                clickTimer = setTimeout(function() {
                    clickCount = 0;
                }, 800); // Reset after 800ms if not triple-clicked
            }

            if (clickCount === 3) {
                clearTimeout(clickTimer);
                clickCount = 0;
                toggleTestPanel();
            }
        });
    }
});