// app/static/js/navbar-cat.js
document.addEventListener('DOMContentLoaded', function() {
    const cat = document.getElementById('navbar-cat');
    if (!cat) return;

    // Cat states
    const states = ['sitting', 'running', 'sleeping', 'eating', 'playing'];
    let currentState = 'sitting';
    let isRunning = false;
    let runningDirection = 1; // 1 for right, -1 for left
    let position = 0;
    const maxPosition = window.innerWidth - 100; // Prevent cat from going off screen

    // Initial state
    setCatState('sitting');

    // Randomly change cat state
    function randomStateChange() {
        // If currently running, increase chance to stop
        if (currentState === 'running') {
            if (Math.random() < 0.3) {
                isRunning = false;
                setCatState('sitting');
                setTimeout(randomStateChange, getRandomTime());
                return;
            }
        } else {
            // Randomly select a new state
            const randomIndex = Math.floor(Math.random() * states.length);
            const newState = states[randomIndex];

            // If switching to running
            if (newState === 'running' && currentState !== 'running') {
                isRunning = true;
                setCatState('running');
                moveWhileRunning();
            } else {
                setCatState(newState);
            }
        }

        // Schedule next state change
        setTimeout(randomStateChange, getRandomTime());
    }

    // Set cat animation state
    function setCatState(state) {
        // Remove all state classes
        states.forEach(s => cat.classList.remove(`cat-${s}`));

        // Add new state class
        cat.classList.add(`cat-${state}`);
        currentState = state;

        // For running, set direction
        if (state === 'running') {
            if (runningDirection === 1) {
                cat.classList.remove('flip-horizontal');
            } else {
                cat.classList.add('flip-horizontal');
            }
        }
    }

    // Move cat while in running state
    function moveWhileRunning() {
        if (!isRunning) return;

        // Update position
        position += 5 * runningDirection;

        // Check boundaries
        if (position >= maxPosition) {
            position = maxPosition;
            runningDirection = -1;
            cat.classList.add('flip-horizontal');
        } else if (position <= 0) {
            position = 0;
            runningDirection = 1;
            cat.classList.remove('flip-horizontal');
        }

        // Apply position
        cat.style.left = `${position}px`;

        // Continue movement if still running
        if (isRunning) {
            requestAnimationFrame(moveWhileRunning);
        }
    }

    // Get random time for state changes (2-10 seconds)
    function getRandomTime() {
        return 2000 + Math.random() * 8000;
    }

    // Make cat interactive
    cat.addEventListener('click', function() {
        // Stop any current movement
        isRunning = false;

        // Play a special animation when clicked
        setCatState('playing');

        // Reset after a moment
        setTimeout(() => {
            setCatState('sitting');
            setTimeout(randomStateChange, getRandomTime());
        }, 2000);
    });

    // Initial state change
    setTimeout(randomStateChange, getRandomTime());
});