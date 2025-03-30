// app/static/js/notes.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize notes functionality
    initNotesBoard();
    initColorPicker();
    initNoteActions();
    checkEmptyState();
});

/**
 * Check if notes container is empty and update CSS class
 */
function checkEmptyState() {
    const notesBoard = document.getElementById('notesBoard');
    if (!notesBoard) return;

    // Count visible notes (could be filtered)
    const visibleNotes = Array.from(notesBoard.querySelectorAll('.sticky-note')).filter(note => {
        return window.getComputedStyle(note).display !== 'none';
    });

    if (visibleNotes.length === 0) {
        notesBoard.classList.add('filtered-empty');
    } else {
        notesBoard.classList.remove('filtered-empty');
    }
}

/**
 * Initialize the interactive notes board
 */
function initNotesBoard() {
    // Get the notes container
    const notesBoard = document.getElementById('notesBoard');
    if (!notesBoard) return;

    // Make notes draggable with interact.js
    interact('.sticky-note').draggable({
        inertia: true,
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: '#notesBoard',
                endOnly: false,
                elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
            })
        ],
        autoScroll: true,
        listeners: {
            start: function(event) {
                // Bring to front when starting drag
                bringToFront(event.target);
            },
            move: dragMoveListener,
            end: dragEndListener
        }
    });

    // Double-click on board to create note at position
    notesBoard.addEventListener('dblclick', function(event) {
        if (event.target === notesBoard) {
            const rect = notesBoard.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            // Get the color from the color picker
            const selectedColor = document.getElementById('noteColor').value;

            // Create a temporary text input for content
            const tempInput = document.createElement('div');
            tempInput.style.position = 'absolute';
            tempInput.style.left = x + 'px';
            tempInput.style.top = y + 'px';
            tempInput.style.zIndex = '1000';
            tempInput.style.background = selectedColor;
            tempInput.style.padding = '15px';
            tempInput.style.borderRadius = '5px';
            tempInput.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.2)';
            tempInput.style.minWidth = '220px';
            tempInput.style.minHeight = '150px';

            const titleInput = document.createElement('input');
            titleInput.type = 'text';
            titleInput.placeholder = 'Title (optional)';
            titleInput.style.width = '100%';
            titleInput.style.padding = '5px';
            titleInput.style.marginBottom = '10px';
            titleInput.style.border = 'none';
            titleInput.style.borderBottom = '1px solid rgba(0, 0, 0, 0.1)';
            titleInput.style.backgroundColor = 'transparent';
            titleInput.style.fontFamily = "'McLaren', sans-serif";
            titleInput.style.fontSize = '16px';
            titleInput.style.fontWeight = 'bold';
            titleInput.style.outline = 'none';

            const textarea = document.createElement('textarea');
            textarea.style.width = '100%';
            textarea.style.height = '100px';
            textarea.style.border = 'none';
            textarea.style.background = 'transparent';
            textarea.style.outline = 'none';
            textarea.style.fontFamily = "'McLaren', sans-serif";
            textarea.style.resize = 'none';
            textarea.placeholder = 'Type your note here...';

            const tagsInput = document.createElement('input');
            tagsInput.type = 'text';
            tagsInput.placeholder = 'Tags (comma separated)';
            tagsInput.style.width = '100%';
            tagsInput.style.padding = '5px';
            tagsInput.style.marginTop = '10px';
            tagsInput.style.border = 'none';
            tagsInput.style.borderTop = '1px solid rgba(0, 0, 0, 0.1)';
            tagsInput.style.backgroundColor = 'transparent';
            tagsInput.style.fontFamily = "'McLaren', sans-serif";
            tagsInput.style.fontSize = '12px';
            tagsInput.style.outline = 'none';

            const buttonsContainer = document.createElement('div');
            buttonsContainer.style.display = 'flex';
            buttonsContainer.style.justifyContent = 'flex-end';
            buttonsContainer.style.marginTop = '10px';

            const cancelButton = document.createElement('button');
            cancelButton.textContent = 'Cancel';
            cancelButton.style.padding = '5px 10px';
            cancelButton.style.backgroundColor = 'transparent';
            cancelButton.style.border = '1px solid rgba(0, 0, 0, 0.2)';
            cancelButton.style.borderRadius = '5px';
            cancelButton.style.marginRight = '5px';
            cancelButton.style.cursor = 'pointer';

            const saveButton = document.createElement('button');
            saveButton.textContent = 'Save';
            saveButton.style.padding = '5px 10px';
            saveButton.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
            saveButton.style.border = '1px solid rgba(0, 0, 0, 0.2)';
            saveButton.style.borderRadius = '5px';
            saveButton.style.cursor = 'pointer';

            buttonsContainer.appendChild(cancelButton);
            buttonsContainer.appendChild(saveButton);

            tempInput.appendChild(titleInput);
            tempInput.appendChild(textarea);
            tempInput.appendChild(tagsInput);
            tempInput.appendChild(buttonsContainer);
            notesBoard.appendChild(tempInput);

            textarea.focus();

            // Cancel on button click
            cancelButton.addEventListener('click', function() {
                notesBoard.removeChild(tempInput);
            });

            // Save on button click
            saveButton.addEventListener('click', function() {
                if (textarea.value.trim() !== '') {
                    createNoteAtPosition(
                        titleInput.value.trim(),
                        textarea.value.trim(),
                        tagsInput.value.trim(),
                        selectedColor,
                        x,
                        y,
                        false
                    );
                }
                notesBoard.removeChild(tempInput);
            });

            // Save on Enter key in textarea (Shift+Enter for new line)
            textarea.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey && document.activeElement === textarea) {
                    e.preventDefault();
                    saveButton.click();
                }
            });
        }
    });

    // Initialize click listeners for all sticky notes
    document.addEventListener('click', function(e) {
        const note = e.target.closest('.sticky-note, .masonry-note');
        if (note && e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
            // Bring to front when clicking on a note (only in board view)
            if (note.classList.contains('sticky-note')) {
                bringToFront(note);
            }
        }
    });
}

/**
 * Initialize the color picker functionality
 */
function initColorPicker() {
    // Create note color picker
    const colorOptions = document.querySelectorAll('.color-picker .color-option');
    colorOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options
            const parent = this.closest('.color-picker');
            parent.querySelectorAll('.color-option').forEach(opt => {
                opt.classList.remove('selected');
            });

            // Add selected class to clicked option
            this.classList.add('selected');

            // Set the hidden input value
            const colorInput = parent.classList.contains('edit-color-picker')
                ? document.getElementById('editNoteColor')
                : document.getElementById('noteColor');

            colorInput.value = this.getAttribute('data-color');

            // If this is in the edit modal, update the preview
            if (parent.classList.contains('edit-color-picker')) {
                const editModal = document.getElementById('editNoteModal');
                if (editModal) {
                    editModal.querySelector('.modal-content').style.backgroundColor = this.getAttribute('data-color');
                }
            }
        });
    });
}

/**
 * Initialize event listeners for note actions (edit, delete, pin, etc)
 */
function initNoteActions() {
    // Form submission for manual form
    const createNoteForm = document.getElementById('createNoteForm');
    if (createNoteForm) {
        createNoteForm.addEventListener('submit', function(e) {
            const content = document.getElementById('noteContent').value.trim();

            if (content === '') {
                e.preventDefault();
                alert('Note content cannot be empty');
                return false;
            }

            // Calculate center position for new notes
            const notesBoard = document.getElementById('notesBoard');
            if (notesBoard) {
                const boardWidth = notesBoard.clientWidth;
                const boardHeight = notesBoard.clientHeight;

                // Center position with slight random offset for stacking
                const posX = Math.max(10, Math.floor(boardWidth / 2 - 100 + (Math.random() * 40 - 20)));
                const posY = Math.max(10, Math.floor(boardHeight / 2 - 100 + (Math.random() * 40 - 20)));

                document.getElementById('positionX').value = posX;
                document.getElementById('positionY').value = posY;
            }

            return true;
        });
    }

    // Pin button click
    document.addEventListener('click', function(e) {
        if (e.target && e.target.closest('.pin-note')) {
            const button = e.target.closest('.pin-note');
            const noteId = button.getAttribute('data-note-id');
            const note = document.querySelector(`.sticky-note[data-id="${noteId}"], .masonry-note[data-id="${noteId}"]`);

            // Toggle pin status via AJAX
            fetch(`/notes/${noteId}/toggle_pin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    if (data.is_pinned) {
                        note.classList.add('is-pinned');
                    } else {
                        note.classList.remove('is-pinned');
                    }
                }
            })
            .catch(error => {
                console.error('Error toggling pin status:', error);
            });
        }
    });

    // Bring to front button click
    document.addEventListener('click', function(e) {
        if (e.target && e.target.closest('.front-note')) {
            const button = e.target.closest('.front-note');
            const noteId = button.getAttribute('data-note-id');
            const note = document.querySelector(`.sticky-note[data-id="${noteId}"]`);

            if (note) {
                // Send to server
                fetch(`/notes/bring_to_front/${noteId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update z-index
                        note.style.zIndex = data.z_index;
                    }
                })
                .catch(error => {
                    console.error('Error bringing note to front:', error);
                });
            }
        }
    });

    // Edit button click
    document.addEventListener('click', function(e) {
        if (e.target && e.target.closest('.edit-note')) {
            const button = e.target.closest('.edit-note');
            const noteId = button.getAttribute('data-note-id');
            const note = document.querySelector(`.sticky-note[data-id="${noteId}"], .masonry-note[data-id="${noteId}"]`);

            if (note) {
                const titleElement = note.querySelector('.note-title');
                const content = note.querySelector('.note-content').textContent;
                const color = note.style.backgroundColor;
                const isPinned = note.classList.contains('is-pinned');

                // Get tags if any
                const tagElements = note.querySelectorAll('.note-tag');
                const tags = Array.from(tagElements).map(tag => tag.textContent).join(', ');

                // Set values in the edit modal
                document.getElementById('editNoteTitle').value = titleElement ? titleElement.textContent : '';
                document.getElementById('editNoteContent').value = content;
                document.getElementById('editNoteTags').value = tags;
                document.getElementById('editNoteColor').value = rgbToHex(color);
                document.getElementById('editNotePinned').checked = isPinned;

                // Highlight the corresponding color option
                const editColorOptions = document.querySelectorAll('.edit-color-picker .color-option');
                editColorOptions.forEach(option => {
                    option.classList.remove('selected');
                    if (option.getAttribute('data-color') === rgbToHex(color)) {
                        option.classList.add('selected');
                    }
                });

                // Update modal background color
                const editModal = document.getElementById('editNoteModal');
                if (editModal) {
                    editModal.querySelector('.modal-content').style.backgroundColor = color;
                }

                // Set the note ID as a data attribute on the save button
                document.getElementById('saveNoteChanges').setAttribute('data-note-id', noteId);

                // Show the modal
                const editNoteModal = new bootstrap.Modal(document.getElementById('editNoteModal'));
                editNoteModal.show();
            }
        }
    });

    // Save note changes
    document.getElementById('saveNoteChanges').addEventListener('click', function() {
        const noteId = this.getAttribute('data-note-id');
        const title = document.getElementById('editNoteTitle').value.trim();
        const content = document.getElementById('editNoteContent').value.trim();
        const tags = document.getElementById('editNoteTags').value.trim();
        const color = document.getElementById('editNoteColor').value;
        const isPinned = document.getElementById('editNotePinned').checked;

        if (content === '') {
            alert('Note content cannot be empty');
            return;
        }

        // Update the note via AJAX
        updateNote(noteId, title, content, tags, color, null, null, null, isPinned);

        // Close the modal
        const editNoteModal = bootstrap.Modal.getInstance(document.getElementById('editNoteModal'));
        editNoteModal.hide();
    });

    // Delete button click
    document.addEventListener('click', function(e) {
        if (e.target && e.target.closest('.delete-note')) {
            const button = e.target.closest('.delete-note');
            const noteId = button.getAttribute('data-note-id');

            // Set the note ID as a data attribute on the confirm button
            document.getElementById('confirmDeleteNote').setAttribute('data-note-id', noteId);

            // Show the modal
            const deleteNoteModal = new bootstrap.Modal(document.getElementById('deleteNoteModal'));
            deleteNoteModal.show();
        }
    });

    // Confirm delete
    document.getElementById('confirmDeleteNote').addEventListener('click', function() {
        const noteId = this.getAttribute('data-note-id');

        // Delete the note via AJAX
        deleteNote(noteId);

        // Close the modal
        const deleteNoteModal = bootstrap.Modal.getInstance(document.getElementById('deleteNoteModal'));
        deleteNoteModal.hide();
    });
}

/**
 * Create a note at a specific position via AJAX
 */
function createNoteAtPosition(title, content, tags, color, x, y, isPinned) {
    // Create the note via AJAX
    fetch('/notes/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            title: title,
            content: content,
            tags: tags,
            color: color,
            position_x: x,
            position_y: y,
            is_pinned: isPinned
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Add the new note to the board
            addNoteToBoard(data.note);
            checkEmptyState();
        } else {
            alert(data.message || 'Error creating note');
        }
    })
    .catch(error => {
        console.error('Error creating note:', error);
        alert('An error occurred while creating the note. Please try again.');
    });
}

/**
 * Add a note to the board
 */
function addNoteToBoard(note) {
    // Add to the board view
    const notesBoard = document.getElementById('notesBoard');
    if (notesBoard) {
        // Create note element
        const noteElement = document.createElement('div');
        noteElement.className = `sticky-note ${note.is_pinned ? 'is-pinned' : ''}`;
        noteElement.id = `note-${note.id}`;
        noteElement.setAttribute('data-id', note.id);
        noteElement.style.backgroundColor = note.color;
        noteElement.style.left = `${note.position_x}px`;
        noteElement.style.top = `${note.position_y}px`;
        noteElement.style.zIndex = note.z_index;

        const formattedDate = new Date(note.updated_at).toLocaleString(undefined, {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });

        // Create inner HTML
        let noteContent = `
            <div class="note-controls">
                <button class="note-btn pin-note" data-note-id="${note.id}" title="${note.is_pinned ? 'Unpin' : 'Pin'} note">
                    <i class="fas fa-thumbtack"></i>
                </button>
                <button class="note-btn front-note" data-note-id="${note.id}" title="Bring to front">
                    <i class="fas fa-arrow-up"></i>
                </button>
                <button class="note-btn edit-note" data-note-id="${note.id}" title="Edit note">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="note-btn delete-note" data-note-id="${note.id}" title="Delete note">
                    <i class="fas fa-trash"></i>
                </button>
            </div>`;

        // Add title if exists
        if (note.title) {
            noteContent += `<div class="note-title">${note.title}</div>`;
        }

        // Add content
        noteContent += `<div class="note-content">${note.content}</div>`;

        // Add tags if exists
        if (note.tags) {
            const tagList = note.tags.split(',').map(tag => tag.trim());
            if (tagList.length > 0) {
                noteContent += '<div class="note-tags">';
                tagList.forEach(tag => {
                    noteContent += `<span class="note-tag" title="${tag}">${tag}</span>`;
                });
                noteContent += '</div>';
            }
        }

        // Add footer
        noteContent += `
            <div class="note-footer">
                <div class="note-timestamp">${formattedDate}</div>
            </div>
        `;

        noteElement.innerHTML = noteContent;
        notesBoard.appendChild(noteElement);

        // Make the new note draggable
        interact(`#note-${note.id}`).draggable({
            inertia: true,
            modifiers: [
                interact.modifiers.restrictRect({
                    restriction: '#notesBoard',
                    endOnly: false,
                    elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
                })
            ],
            autoScroll: true,
            listeners: {
                start: function(event) {
                    // Bring to front when starting drag
                    bringToFront(event.target);
                },
                move: dragMoveListener,
                end: dragEndListener
            }
        });
    }

    // Add to the list view
    const notesMasonry = document.querySelector('.notes-masonry');
    if (notesMasonry) {
        // Create note element
        const masonryNote = document.createElement('div');
        masonryNote.className = `masonry-note ${note.is_pinned ? 'is-pinned' : ''}`;
        masonryNote.setAttribute('data-id', note.id);
        masonryNote.style.backgroundColor = note.color;

        const formattedDate = new Date(note.updated_at).toLocaleString(undefined, {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });

        // Create inner HTML
        let noteContent = `
        <div class="masonry-note-content">
            <div class="note-controls">
                <button class="note-btn pin-note" data-note-id="${note.id}" title="${note.is_pinned ? 'Unpin' : 'Pin'} note">
                    <i class="fas fa-thumbtack"></i>
                </button>
                <button class="note-btn edit-note" data-note-id="${note.id}" title="Edit note">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="note-btn delete-note" data-note-id="${note.id}" title="Delete note">
                    <i class="fas fa-trash"></i>
                </button>
            </div>`;

        // Add title if exists
        if (note.title) {
            noteContent += `<div class="note-title">${note.title}</div>`;
        }

        // Add content
        noteContent += `<div class="note-content">${note.content}</div>`;

        // Add tags if exists
        if (note.tags) {
            const tagList = note.tags.split(',').map(tag => tag.trim());
            if (tagList.length > 0) {
                noteContent += '<div class="note-tags">';
                tagList.forEach(tag => {
                    noteContent += `<span class="note-tag" title="${tag}">${tag}</span>`;
                });
                noteContent += '</div>';
            }
        }

        // Add footer
        noteContent += `
            <div class="note-footer">
                <div class="note-timestamp">${formattedDate}</div>
            </div>
        </div>`;

        masonryNote.innerHTML = noteContent;

        // Remove empty state if exists
        const emptyState = notesMasonry.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }

        // Add to masonry
        notesMasonry.prepend(masonryNote);
    }
}

/**
 * Update a note
 */
function updateNote(noteId, title, content, tags, color, posX, posY, zIndex, isPinned) {
    const updateData = {
        id: noteId
    };

    if (title !== undefined) updateData.title = title;
    if (content !== undefined) updateData.content = content;
    if (tags !== undefined) updateData.tags = tags;
    if (color !== undefined) updateData.color = color;
    if (posX !== undefined) updateData.position_x = posX;
    if (posY !== undefined) updateData.position_y = posY;
    if (zIndex !== undefined) updateData.z_index = zIndex;
    if (isPinned !== undefined) updateData.is_pinned = isPinned;

    // Send update request
    fetch(`/notes/${noteId}/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(updateData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update board view note
            const boardNote = document.querySelector(`.sticky-note[data-id="${noteId}"]`);
            updateNoteElement(boardNote, data.note);

            // Update list view note
            const listNote = document.querySelector(`.masonry-note[data-id="${noteId}"]`);
            updateNoteElement(listNote, data.note);
        } else {
            alert('Error updating note');
        }
    })
    .catch(error => {
        console.error('Error updating note:', error);
        alert('An error occurred while updating the note. Please try again.');
    });
}

/**
 * Update a note element with new data
 */
function updateNoteElement(noteElement, noteData) {
    if (!noteElement) return;

    // Update basic properties
    noteElement.style.backgroundColor = noteData.color;

    // Update pin status
    if (noteData.is_pinned) {
        noteElement.classList.add('is-pinned');
    } else {
        noteElement.classList.remove('is-pinned');
    }

    // Update title
    let titleElement = noteElement.querySelector('.note-title');
    if (noteData.title) {
        if (titleElement) {
            titleElement.textContent = noteData.title;
        } else {
            // Create title element if it doesn't exist
            titleElement = document.createElement('div');
            titleElement.className = 'note-title';
            titleElement.textContent = noteData.title;

            // Insert after controls (if any) or at the beginning
            const controls = noteElement.querySelector('.note-controls');
            if (controls) {
                controls.after(titleElement);
            } else {
                const content = noteElement.querySelector('.note-content');
                content.before(titleElement);
            }
        }
    } else if (titleElement) {
        // Remove title if it exists but shouldn't
        titleElement.remove();
    }

    // Update content
    const contentElement = noteElement.querySelector('.note-content');
    if (contentElement) {
        contentElement.textContent = noteData.content;
    }

    // Update tags
    const tagsContainer = noteElement.querySelector('.note-tags');
    if (noteData.tags) {
        const tagList = noteData.tags.split(',').map(tag => tag.trim());

        if (tagsContainer) {
            // Update existing tags container
            tagsContainer.innerHTML = '';
            tagList.forEach(tag => {
                const span = document.createElement('span');
                span.className = 'note-tag';
                span.title = tag;
                span.textContent = tag;
                tagsContainer.appendChild(span);
            });
        } else {
            // Create new tags container
            const newTagsContainer = document.createElement('div');
            newTagsContainer.className = 'note-tags';

            tagList.forEach(tag => {
                const span = document.createElement('span');
                span.className = 'note-tag';
                span.title = tag;
                span.textContent = tag;
                newTagsContainer.appendChild(span);
            });

            // Insert before footer
            const footer = noteElement.querySelector('.note-footer');
            if (footer) {
                footer.before(newTagsContainer);
            } else {
                // No footer, append to end
                noteElement.appendChild(newTagsContainer);
            }
        }
    } else if (tagsContainer) {
        // Remove tags container if it exists but shouldn't
        tagsContainer.remove();
    }

    // Update timestamp
    const timestamp = noteElement.querySelector('.note-timestamp');
    if (timestamp) {
        const formattedDate = new Date(noteData.updated_at).toLocaleString(undefined, {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
        timestamp.textContent = formattedDate;
    }

    // Update position and z-index for board view only
    if (noteElement.classList.contains('sticky-note')) {
        if (noteData.position_x !== undefined) {
            noteElement.style.left = `${noteData.position_x}px`;
        }
        if (noteData.position_y !== undefined) {
            noteElement.style.top = `${noteData.position_y}px`;
        }
        if (noteData.z_index !== undefined) {
            noteElement.style.zIndex = noteData.z_index;
        }
    }
}

/**
 * Delete a note
 */
function deleteNote(noteId) {
    fetch(`/notes/${noteId}/delete`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove from board view
            const boardNote = document.querySelector(`.sticky-note[data-id="${noteId}"]`);
            if (boardNote) {
                boardNote.remove();
            }

            // Remove from list view
            const listNote = document.querySelector(`.masonry-note[data-id="${noteId}"]`);
            if (listNote) {
                listNote.remove();
            }

            // Check if we need to show empty state
            const boardNotes = document.querySelectorAll('.sticky-note');
            const masonryNotes = document.querySelectorAll('.masonry-note');

            if (boardNotes.length === 0 || masonryNotes.length === 0) {
                checkEmptyState();
            }
        } else {
            alert('Error deleting note');
        }
    })
    .catch(error => {
        console.error('Error deleting note:', error);
        alert('An error occurred while deleting the note. Please try again.');
    });
}

/**
 * Bring a note to front by updating z-index
 */
function bringToFront(noteElement) {
    if (!noteElement || !noteElement.classList.contains('sticky-note')) return;

    const noteId = noteElement.getAttribute('data-id');

    // Find highest z-index
    const allNotes = document.querySelectorAll('.sticky-note');
    let maxZ = 0;

    allNotes.forEach(note => {
        const zIndex = parseInt(note.style.zIndex || 0);
        if (zIndex > maxZ) {
            maxZ = zIndex;
        }
    });

    // Only update if needed
    const currentZ = parseInt(noteElement.style.zIndex || 0);
    if (currentZ < maxZ) {
        // Update locally first for immediate feedback
        noteElement.style.zIndex = maxZ + 1;

        // Then update on server
        fetch(`/notes/bring_to_front/${noteId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .catch(error => console.error('Error updating z-index:', error));
    }
}

/**
 * Handle note dragging
 */
function dragMoveListener(event) {
    const target = event.target;

    // Keep the dragged position in the data-x/data-y attributes
    const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
    const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

    // Update the element's position
    target.style.transform = `translate(${x}px, ${y}px)`;

    // Store the position
    target.setAttribute('data-x', x);
    target.setAttribute('data-y', y);
}

/**
 * Handle the end of a drag operation
 */
function dragEndListener(event) {
    const target = event.target;
    const noteId = target.getAttribute('data-id');

    // Calculate the new absolute position
    const x = (parseFloat(target.getAttribute('data-x')) || 0);
    const y = (parseFloat(target.getAttribute('data-y')) || 0);

    // Get the initial position from the inline styles
    const initialX = parseInt(target.style.left) || 0;
    const initialY = parseInt(target.style.top) || 0;

    // Calculate the final position
    const finalX = initialX + x;
    const finalY = initialY + y;

    // Make sure positions are within bounds
    const notesBoard = document.getElementById('notesBoard');
    const maxX = notesBoard.clientWidth - target.offsetWidth;
    const maxY = notesBoard.clientHeight - target.offsetHeight;

    const boundedX = Math.max(0, Math.min(finalX, maxX));
    const boundedY = Math.max(0, Math.min(finalY, maxY));

    // Update the note position in the database
    updateNote(noteId, undefined, undefined, undefined, undefined, boundedX, boundedY);

    // Update the inline styles and reset the transform
    target.style.left = `${boundedX}px`;
    target.style.top = `${boundedY}px`;
    target.style.transform = '';
    target.setAttribute('data-x', 0);
    target.setAttribute('data-y', 0);
}

/**
 * Convert RGB color to HEX format
 */
function rgbToHex(rgb) {
    // If the color is already in hex format
    if (rgb.startsWith('#')) {
        return rgb;
    }

    // Extract RGB values
    const rgbMatch = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    if (!rgbMatch) return '#fff740'; // Default if format is not recognized

    // Convert RGB components to hex
    function componentToHex(c) {
        const hex = parseInt(c).toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    }

    return '#' + componentToHex(rgbMatch[1]) + componentToHex(rgbMatch[2]) + componentToHex(rgbMatch[3]);
}