/**
 * Diary functionality
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

                    // Show notification
                    const toast = document.createElement('div');
                    toast.className = 'position-fixed bottom-0 end-0 p-3';
                    toast.style.zIndex = '5';
                    toast.innerHTML = `
                        <div class="toast align-items-center text-white bg-${data.is_favorite ? 'primary' : 'secondary'}" role="alert" aria-live="assertive" aria-atomic="true">
                            <div class="d-flex">
                                <div class="toast-body">
                                    ${data.message}
                                </div>
                                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                            </div>
                        </div>
                    `;
                    document.body.appendChild(toast);

                    // Initialize and show the toast
                    const toastEl = new bootstrap.Toast(toast.querySelector('.toast'), { autohide: true, delay: 3000 });
                    toastEl.show();

                    // Remove toast element after it's hidden
                    toast.querySelector('.toast').addEventListener('hidden.bs.toast', function() {
                        document.body.removeChild(toast);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Mood selector UI enhancement
    const moodSelectors = document.querySelectorAll('.mood-option');
    const moodInput = document.getElementById('mood');

    if (moodSelectors.length && moodInput) {
        // Set the initial selected mood if there is one
        const currentMood = moodInput.value;
        if (currentMood) {
            document.querySelector(`.mood-option[data-mood="${currentMood}"]`).classList.add('selected');
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

    if (diaryEntryForm && titleInput && contentInput) {
        // Check if we have a saved draft
        const savedTitle = localStorage.getItem('diary_draft_title');
        const savedContent = localStorage.getItem('diary_draft_content');
        const savedTimestamp = localStorage.getItem('diary_draft_timestamp');

        // If we're on the edit page, don't load draft
        const isEditPage = window.location.href.includes('/edit');

        if (!isEditPage && savedTitle && savedContent && savedTimestamp) {
            const saveTime = new Date(parseInt(savedTimestamp));
            const now = new Date();
            const hoursSinceUpdate = (now - saveTime) / (1000 * 60 * 60);

            // Only restore draft if it's less than 24 hours old
            if (hoursSinceUpdate < 24) {
                // Show draft recovery modal
                const draftModal = new bootstrap.Modal(document.getElementById('draftRecoveryModal'));

                // Set timestamp in modal
                document.getElementById('draftTimestamp').textContent = saveTime.toLocaleString();

                // Set up buttons
                document.getElementById('restoreDraftBtn').addEventListener('click', function() {
                    titleInput.value = savedTitle;
                    contentInput.value = savedContent;
                    draftModal.hide();
                });

                document.getElementById('discardDraftBtn').addEventListener('click', function() {
                    localStorage.removeItem('diary_draft_title');
                    localStorage.removeItem('diary_draft_content');
                    localStorage.removeItem('diary_draft_timestamp');
                    draftModal.hide();
                });

                draftModal.show();
            }
        }

        // Set up auto-save
        let autoSaveTimeout;

        const saveDraft = () => {
            const title = titleInput.value.trim();
            const content = contentInput.value.trim();

            if (title || content) {
                localStorage.setItem('diary_draft_title', title);
                localStorage.setItem('diary_draft_content', content);
                localStorage.setItem('diary_draft_timestamp', Date.now().toString());

                // Show save indicator
                const saveIndicator = document.getElementById('autosaveIndicator');
                if (saveIndicator) {
                    saveIndicator.textContent = 'Draft saved';
                    saveIndicator.style.opacity = '1';

                    setTimeout(() => {
                        saveIndicator.style.opacity = '0';
                    }, 2000);
                }
            }
        };

        const debouncedSave = () => {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(saveDraft, 1000);
        };

        // Set up event listeners for auto-save
        titleInput.addEventListener('input', debouncedSave);
        contentInput.addEventListener('input', debouncedSave);

        // Clear draft when form is submitted
        diaryEntryForm.addEventListener('submit', function() {
            localStorage.removeItem('diary_draft_title');
            localStorage.removeItem('diary_draft_content');
            localStorage.removeItem('diary_draft_timestamp');
        });
    }

    // Word counter for diary content
    const wordCountElement = document.getElementById('wordCount');
    if (contentInput && wordCountElement) {
        const updateWordCount = () => {
            const text = contentInput.value.trim();
            const wordCount = text ? text.split(/\s+/).length : 0;
            wordCountElement.textContent = `${wordCount} words`;
        };

        // Initial count
        updateWordCount();

        // Update on input
        contentInput.addEventListener('input', updateWordCount);
    }

    // Date range picker for filtering entries
    const dateRangePicker = document.getElementById('dateRangePicker');
    if (dateRangePicker) {
        const dateFrom = document.getElementById('date_from');
        const dateTo = document.getElementById('date_to');

        // Initialize date picker if library is available
        if (typeof flatpickr !== 'undefined') {
            flatpickr(dateRangePicker, {
                mode: 'range',
                dateFormat: 'Y-m-d',
                onChange: function(selectedDates, dateStr, instance) {
                    if (selectedDates.length === 2) {
                        dateFrom.value = formatDate(selectedDates[0]);
                        dateTo.value = formatDate(selectedDates[1]);
                    }
                }
            });
        }

        function formatDate(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
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

    // Handle markdown preview if applicable
    const previewBtn = document.getElementById('previewBtn');
    const editBtn = document.getElementById('editBtn');
    const contentEditor = document.getElementById('content-editor');
    const contentPreview = document.getElementById('content-preview');

    if (previewBtn && editBtn && contentEditor && contentPreview) {
        previewBtn.addEventListener('click', function() {
            // Switch to preview mode
            contentEditor.classList.add('d-none');
            contentPreview.classList.remove('d-none');

            // Set active button
            previewBtn.classList.add('active');
            editBtn.classList.remove('active');

            // Convert markdown to HTML if marked library is available
            if (typeof marked !== 'undefined') {
                contentPreview.innerHTML = marked.parse(contentInput.value);
            } else {
                // Simple fallback with line breaks
                contentPreview.innerHTML = contentInput.value.replace(/\n/g, '<br>');
            }
        });

        editBtn.addEventListener('click', function() {
            // Switch to edit mode
            contentEditor.classList.remove('d-none');
            contentPreview.classList.add('d-none');

            // Set active button
            editBtn.classList.add('active');
            previewBtn.classList.remove('active');
        });
    }
});