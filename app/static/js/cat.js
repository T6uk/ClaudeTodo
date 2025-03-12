function initCat() {
  // Cat elements
  const catWrapper = document.querySelector('.cat_wrapper');
  const navbarContainer = document.querySelector('.navbar-cat-container');
  const cat = document.querySelector('.cat');
  const head = document.querySelector('.cat_head');
  const legs = document.querySelectorAll('.leg');
  const body = document.querySelector('.body');

  // States and properties
  const pos = {
    x: null,
    y: null,
    targetX: null,
    lastActivity: Date.now()
  };

  const state = {
    action: 'idle',   // idle, walking, running, sleeping, eating, grooming
    isMoving: false,
    isJumping: false,
    lastMoodChange: Date.now()
  };

  // If cat elements don't exist, return
  if (!cat || !catWrapper || !navbarContainer) return;

  // Get navbar dimensions
  const updateNavbarBounds = () => navbarContainer.getBoundingClientRect();
  let navbarBounds = updateNavbarBounds();

  // Add additional elements for animations
  const addElements = () => {
    // Add ZZZ for sleeping
    const zzz = document.createElement('div');
    zzz.className = 'zzz';
    zzz.textContent = 'z';
    catWrapper.appendChild(zzz);

    // Add food bowl for eating
    const foodBowl = document.createElement('div');
    foodBowl.className = 'food-bowl';
    catWrapper.appendChild(foodBowl);
  };

  // Set initial position
  const initPosition = () => {
    cat.style.left = `${navbarBounds.width / 2}px`;
    pos.targetX = navbarBounds.width / 2;
  };

  // Clear all states
  const clearAllStates = () => {
    catWrapper.classList.remove('sleeping', 'eating', 'grooming', 'attentive', 'excited', 'jump');
    legs.forEach(leg => {
      leg.classList.remove('walk', 'run');
    });
    state.isMoving = false;
    state.isJumping = false;
  };

  // Begin walking animation
  const walk = () => {
    if (state.action !== 'walking' && state.action !== 'running') {
      clearAllStates();
      state.action = 'walking';
      state.isMoving = true;
      cat.classList.remove('first_pose');
      legs.forEach(leg => leg.classList.add('walk'));
    }
  };

  // Begin running animation
  const run = () => {
    if (state.action !== 'running') {
      clearAllStates();
      state.action = 'running';
      state.isMoving = true;
      cat.classList.remove('first_pose');
      legs.forEach(leg => leg.classList.add('run'));

      // Make transition faster when running
      cat.style.transition = 'left 0.3s cubic-bezier(0.22, 1, 0.36, 1)';
    }
  };

  // Stop movement animation
  const stopMoving = () => {
    if (state.isMoving) {
      legs.forEach(leg => {
        leg.classList.remove('walk', 'run');
      });
      state.isMoving = false;

      // Reset transition speed
      cat.style.transition = 'left 0.6s cubic-bezier(0.22, 1, 0.36, 1)';
    }
  };

  // Start sleeping animation
  const sleep = () => {
    if (state.action !== 'sleeping') {
      clearAllStates();
      state.action = 'sleeping';
      catWrapper.classList.add('sleeping');
    }
  };

  // Start eating animation
  const eat = () => {
    if (state.action !== 'eating') {
      clearAllStates();
      state.action = 'eating';
      catWrapper.classList.add('eating');

      // Position the food bowl under the cat's head
      const foodBowl = catWrapper.querySelector('.food-bowl');
      if (foodBowl) {
        if (cat.classList.contains('face_right')) {
          foodBowl.style.left = `${parseInt(cat.style.left) + 35}px`;
        } else {
          foodBowl.style.left = `${parseInt(cat.style.left) + 15}px`;
        }
      }
    }
  };

  // Start grooming animation
  const groom = () => {
    if (state.action !== 'grooming') {
      clearAllStates();
      state.action = 'grooming';
      catWrapper.classList.add('grooming');
    }
  };

  // Handle mouse movement
  const handleMouseMotion = e => {
    // Calculate position relative to navbar
    const relativeX = e.clientX - navbarBounds.left;

    // Keep position within navbar bounds with some padding
    if (relativeX > -50 && relativeX < navbarBounds.width + 50) {
      pos.x = relativeX;
      pos.y = e.clientY - navbarBounds.top;
      pos.lastActivity = Date.now();

      // If sleeping or doing something else, wake up with 50% chance
      if (state.action !== 'walking' && state.action !== 'running' && Math.random() > 0.5) {
        walk();
      }

      // Don't immediately move to new position, just update target
      pos.targetX = pos.x;
    }
  };

  // Handle click - cat runs to click position
  const handleClick = e => {
    // Calculate position relative to navbar
    const relativeX = e.clientX - navbarBounds.left;

    // Keep position within navbar bounds
    if (relativeX > 0 && relativeX < navbarBounds.width) {
      pos.targetX = relativeX;
      pos.lastActivity = Date.now();

      // Run to clicked position
      run();
    }
  };

  // Turn cat to face right
  const turnRight = () => {
    cat.classList.remove('face_left');
    cat.classList.add('face_right');

    // Adjust food bowl position when direction changes
    if (state.action === 'eating') {
      const foodBowl = catWrapper.querySelector('.food-bowl');
      if (foodBowl) {
        foodBowl.style.left = `${parseInt(cat.style.left) + 35}px`;
      }
    }
  };

  // Turn cat to face left
  const turnLeft = () => {
    cat.classList.remove('face_right');
    cat.classList.add('face_left');

    // Adjust food bowl position when direction changes
    if (state.action === 'eating') {
      const foodBowl = catWrapper.querySelector('.food-bowl');
      if (foodBowl) {
        foodBowl.style.left = `${parseInt(cat.style.left) + 15}px`;
      }
    }
  };

  // Move the cat based on current action
  const moveCat = () => {
    if (!pos.targetX) return;

    const catX = parseInt(cat.style.left) || 0;
    const catCenter = catX + (cat.offsetWidth / 2);
    const distance = pos.targetX - catCenter;
    const absDistance = Math.abs(distance);

    // Determine if we should move
    if (absDistance > 5) {
      // Set direction
      if (distance > 0) {
        turnRight();
      } else {
        turnLeft();
      }

      // Calculate move speed based on distance and action
      let moveSpeed = 0;
      if (state.action === 'running') {
        moveSpeed = Math.min(absDistance * 0.3, 30); // Faster for running
      } else if (state.action === 'walking') {
        moveSpeed = Math.min(absDistance * 0.1, 10); // Slower for walking
      }

      // Apply movement if we're moving
      if (state.isMoving && moveSpeed > 0) {
        const newPos = catX + Math.sign(distance) * moveSpeed;
        cat.style.left = `${newPos}px`;
      }
    } else if (state.isMoving) {
      // We've reached the target, stop moving
      stopMoving();

      // 20% chance to do something else when reached target
      if (Math.random() > 0.8) {
        chooseRandomAction();
      }
    }
  };

  // Cat jumps
  const jump = () => {
    if (state.isJumping || state.action === 'sleeping') return;

    state.isJumping = true;
    catWrapper.classList.add('jump');

    // Remove jump class after animation completes
    setTimeout(() => {
      catWrapper.classList.remove('jump');
      state.isJumping = false;
    }, 800);
  };

  // Cat shows attentive behavior
  const showAttention = () => {
    catWrapper.classList.add('attentive');
    setTimeout(() => {
      catWrapper.classList.remove('attentive');
    }, 500);
  };

  // Choose a random action based on current state
  const chooseRandomAction = () => {
    // Don't change mood too frequently
    if (Date.now() - state.lastMoodChange < 5000) return;

    const actions = [];

    // Add possible next states based on current state
    if (state.action === 'idle' || state.action === 'walking') {
      actions.push(
        { action: sleep, weight: 3 },
        { action: eat, weight: 2 },
        { action: groom, weight: 2 },
        { action: showAttention, weight: 1 },
        { action: jump, weight: 1 }
      );
    } else if (state.action === 'sleeping') {
      // Less likely to wake up
      if (Math.random() > 0.7) {
        actions.push(
          { action: walk, weight: 2 },
          { action: groom, weight: 3 },
          { action: showAttention, weight: 1 }
        );
      }
    } else if (state.action === 'eating') {
      actions.push(
        { action: walk, weight: 2 },
        { action: sleep, weight: 3 },
        { action: groom, weight: 2 }
      );
    } else if (state.action === 'grooming') {
      actions.push(
        { action: walk, weight: 2 },
        { action: sleep, weight: 3 },
        { action: eat, weight: 1 },
        { action: showAttention, weight: 1 }
      );
    }

    // Select a random action based on weights
    if (actions.length > 0) {
      const totalWeight = actions.reduce((sum, action) => sum + action.weight, 0);
      let random = Math.random() * totalWeight;

      for (const action of actions) {
        random -= action.weight;
        if (random <= 0) {
          action.action();
          state.lastMoodChange = Date.now();
          break;
        }
      }
    }
  };

  // Check inactivity and possibly do something else
  const checkInactivity = () => {
    const inactiveTime = Date.now() - pos.lastActivity;

    // If mouse hasn't moved for a while, cat gets bored
    if (inactiveTime > 5000 && Math.random() > 0.7) {
      chooseRandomAction();
    }

    // If inactive for a long time and not already sleeping, go to sleep
    if (inactiveTime > 15000 && state.action !== 'sleeping' && Math.random() > 0.5) {
      sleep();
    }
  };

  // Handle window resize
  const handleResize = () => {
    navbarBounds = updateNavbarBounds();

    // Make sure cat stays within bounds after resize
    const catX = parseInt(cat.style.left) || 0;
    if (catX > navbarBounds.width - 50) {
      cat.style.left = `${navbarBounds.width - 50}px`;
    }
  };

  // Update loop - runs every frame
  const update = () => {
    if (state.action === 'walking' || state.action === 'running') {
      moveCat();
    }

    // Check if we should change what we're doing
    checkInactivity();

    // Schedule next update
    requestAnimationFrame(update);
  };

  // Occasionally do something random
  const randomAction = () => {
    // Only if not actively following the mouse
    if (Date.now() - pos.lastActivity > 3000) {
      // Sometimes move to a random position
      if (Math.random() > 0.7 && (state.action === 'idle' || state.action === 'walking')) {
        pos.targetX = Math.random() * navbarBounds.width;
        walk();
      } else {
        // Or choose a random action
        chooseRandomAction();
      }
    }
  };

  // Start the cat
  const init = () => {
    addElements();
    initPosition();

    // Event listeners
    document.addEventListener('mousemove', handleMouseMotion);
    navbarContainer.addEventListener('click', handleClick);
    window.addEventListener('resize', handleResize);

    // Start update loop
    update();

    // Set up random action interval
    setInterval(randomAction, 5000);
  };

  // Initialize
  init();
}

// Initialize cat animation after DOM is loaded
window.addEventListener('DOMContentLoaded', function() {
  setTimeout(initCat, 300);
});