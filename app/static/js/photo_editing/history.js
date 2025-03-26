// app/static/js/photo_editing/history.js

/**
 * History management for photo editing
 */
class HistoryManager {
    constructor(maxHistorySize = 20) {
        this.history = [];
        this.currentIndex = -1;
        this.maxHistorySize = maxHistorySize;
    }

    // Add a new state to history
    addState(imageData) {
        // If we're not at the end of the history, truncate
        if (this.currentIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.currentIndex + 1);
        }

        // Add the new state
        this.history.push(imageData);
        this.currentIndex++;

        // Limit history size
        if (this.history.length > this.maxHistorySize) {
            this.history.shift();
            this.currentIndex--;
        }

        // Enable/disable undo/redo buttons
        this.updateButtonStates();
    }

    // Undo to previous state
    undo() {
        if (this.canUndo()) {
            this.currentIndex--;
            const prevState = this.history[this.currentIndex];
            this.updateButtonStates();
            return prevState;
        }
        return null;
    }

    // Redo to next state
    redo() {
        if (this.canRedo()) {
            this.currentIndex++;
            const nextState = this.history[this.currentIndex];
            this.updateButtonStates();
            return nextState;
        }
        return null;
    }

    // Check if undo is available
    canUndo() {
        return this.currentIndex > 0;
    }

    // Check if redo is available
    canRedo() {
        return this.currentIndex < this.history.length - 1;
    }

    // Update undo/redo button states
    updateButtonStates() {
        const undoBtn = document.getElementById('history-undo-btn');
        const redoBtn = document.getElementById('history-redo-btn');

        if (undoBtn) {
            undoBtn.disabled = !this.canUndo();
        }
        if (redoBtn) {
            redoBtn.disabled = !this.canRedo();
        }
    }

    // Reset history
    reset() {
        this.history = [];
        this.currentIndex = -1;
        this.updateButtonStates();
    }
}

// Initialize the history manager when the window loads
window.addEventListener('load', () => {
    window.historyManager = new HistoryManager();
});