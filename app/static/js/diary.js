// app/static/js/diary.js (updated)
/**
 * Enhanced Diary functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Toggle favorite status
    const favoriteStars = document.querySelectorAll('.favorite-star');

    favoriteStars.forEach(star => {
        star.addEventListener('click', function() {
            const entryId = this.getAttribute('data-entry-id');

            fetch(`/diary/${entryId}/toggle-favorite`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update star appearance
                    if (data.is_favorite) {
                        this.classList.remove('far', 'not-favorite');
                        this.classList.add('fas');
                    } else {
                        this.classList.remove('fas');
                        this.classList.add('far', 'not-favorite');
                    }

                    // Show toast notification
                    showToast(data.message, data.is_favorite ? 'primary' : 'secondary');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Failed to update favorite status', 'danger');
            });
        });
    });

    // Simple toast notification function
    function showToast(message, type = 'primary') {
        const toast = document.createElement('div');
        toast.className = 'position-fixed bottom-0 end-0 p-3';
        toast.style.zIndex = '5';
        toast.innerHTML = `
            <div class="toast align-items-center text-white bg-${type}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        document.body.appendChild(toast);

        // Initialize and show the toast if Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
            const toastEl = new bootstrap.Toast(toast.querySelector('.toast'), { autohide: true, delay: 3000 });
            toastEl.show();

            // Remove toast element after it's hidden
            toast.querySelector('.toast').addEventListener('hidden.bs.toast', function() {
                document.body.removeChild(toast);
            });
        } else {
            // Fallback if Bootstrap isn't available
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 3000);
        }
    }

    // Mood selector UI enhancement
    const moodSelectors = document.querySelectorAll('.mood-option');
    const moodInput = document.getElementById('mood');

    if (moodSelectors.length && moodInput) {
        // Set the initial selected mood if there is one
        const currentMood = moodInput.value;
        if (currentMood) {
            document.querySelector(`.mood-option[data-mood="${currentMood}"]`)?.classList.add('selected');
        }

        moodSelectors.forEach(selector => {
            selector.addEventListener('click', function() {
                // Remove selected class from all options
                moodSelectors.forEach(opt => opt.classList.remove('selected'));

                // Add selected class to clicked option
                this.classList.add('selected');

                // Update hidden input
                moodInput.value = this.getAttribute('data-mood');
            });
        });
    }

    // Auto-save draft using localStorage
    const diaryEntryForm = document.getElementById('diaryEntryForm');
    const titleInput = document.getElementById('title');
    const contentInput = document.getElementById('content');
    const autosaveIndicator = document.getElementById('autosaveIndicator');

    if (diaryEntryForm && titleInput && contentInput) {
        const STORAGE_PREFIX = 'diary_draft_';
        const AUTOSAVE_INTERVAL = 10000; // 10 seconds
        let autoSaveTimer;
        let lastSaved = {
            title: titleInput.value,
            content: contentInput.value
        };

        // Draft recovery functionality
        // Check if we have a saved draft
        const savedTitle = localStorage.getItem(`${STORAGE_PREFIX}title`);
        const savedContent = localStorage.getItem(`${STORAGE_PREFIX}content`);
        const savedTimestamp = localStorage.getItem(`${STORAGE_PREFIX}timestamp`);
        const draftRecoveryModal = document.getElementById('draftRecoveryModal');

        // If we're on the edit page, don't load draft
        const isEditPage = window.location.href.includes('/edit');

        if (!isEditPage && savedTitle && savedContent && savedTimestamp && draftRecoveryModal) {
            const saveTime = new Date(parseInt(savedTimestamp));
            const now = new Date();
            const hoursSinceUpdate = (now - saveTime) / (1000 * 60 * 60);

            // Only restore draft if it's less than 24 hours old
            if (hoursSinceUpdate < 24) {
                // Show draft recovery modal
                const draftModal = new bootstrap.Modal(draftRecoveryModal);

                // Set timestamp in modal
                const draftTimestampEl = document.getElementById('draftTimestamp');
                if (draftTimestampEl) {
                    draftTimestampEl.textContent = saveTime.toLocaleString();
                }

                // Set up buttons
                const restoreDraftBtn = document.getElementById('restoreDraftBtn');
                const discardDraftBtn = document.getElementById('discardDraftBtn');

                if (restoreDraftBtn) {
                    restoreDraftBtn.addEventListener('click', function() {
                        titleInput.value = savedTitle;
                        contentInput.value = savedContent;
                        draftModal.hide();

                        // Update word count
                        updateWordCount();
                    });
                }

                if (discardDraftBtn) {
                    discardDraftBtn.addEventListener('click', function() {
                        clearSavedDraft();
                        draftModal.hide();
                    });
                }

                draftModal.show();
            } else {
                // Draft too old, clear it
                clearSavedDraft();
            }
        }

        // Set up auto-save
        function saveDraft() {
            const title = titleInput.value.trim();
            const content = contentInput.value.trim();

            // Only save if content changed
            if (title !== lastSaved.title || content !== lastSaved.content) {
                if (title || content) {
                    localStorage.setItem(`${STORAGE_PREFIX}title`, title);
                    localStorage.setItem(`${STORAGE_PREFIX}content`, content);
                    localStorage.setItem(`${STORAGE_PREFIX}timestamp`, Date.now().toString());

                    lastSaved.title = title;
                    lastSaved.content = content;

                    // Show save indicator
                    if (autosaveIndicator) {
                        autosaveIndicator.textContent = 'Draft saved';
                        autosaveIndicator.classList.remove('d-none');

                        setTimeout(() => {
                            autosaveIndicator.classList.add('d-none');
                        }, 2000);
                    }
                }
            }
        }

        function clearSavedDraft() {
            localStorage.removeItem(`${STORAGE_PREFIX}title`);
            localStorage.removeItem(`${STORAGE_PREFIX}content`);
            localStorage.removeItem(`${STORAGE_PREFIX}timestamp`);
        }

        // Set up event listeners for auto-save
        titleInput.addEventListener('input', scheduleAutosave);
        contentInput.addEventListener('input', scheduleAutosave);

        function scheduleAutosave() {
            clearTimeout(autoSaveTimer);
            autoSaveTimer = setTimeout(saveDraft, 2000);

            // Also update the word count
            updateWordCount();
        }

        // Start the regular autosave interval
        setInterval(saveDraft, AUTOSAVE_INTERVAL);

        // Clear draft when form is submitted
        diaryEntryForm.addEventListener('submit', function() {
            clearSavedDraft();
        });

        // Word count functionality
        const wordCountElement = document.getElementById('wordCount');

        function updateWordCount() {
            if (wordCountElement && contentInput) {
                const text = contentInput.value.trim();
                const wordCount = text ? text.split(/\s+/).filter(word => word.length > 0).length : 0;
                wordCountElement.textContent = `${wordCount} words`;
            }
        }

        // Initial word count
        if (wordCountElement) {
            updateWordCount();
        }
    }

    // Print entry functionality
    const printEntryBtn = document.getElementById('printEntryBtn');
    if (printEntryBtn) {
        printEntryBtn.addEventListener('click', function() {
            window.print();
        });
    }

    // Export entry to text
    const exportEntryBtn = document.getElementById('exportEntryBtn');
    if (exportEntryBtn) {
        exportEntryBtn.addEventListener('click', function() {
            const entryTitle = document.querySelector('.diary-entry-title').textContent;
            const entryDate = document.querySelector('.diary-entry-date').textContent.trim();
            const entryContent = document.querySelector('.diary-entry-content').textContent;

            const text = `${entryTitle}\n${entryDate}\n\n${entryContent}`;

            // Create a temporary link to download the text
            const element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
            element.setAttribute('download', `${entryTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.txt`);

            element.style.display = 'none';
            document.body.appendChild(element);

            element.click();

            document.body.removeChild(element);
        });
    }
});