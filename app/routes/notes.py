"""
Routes for notes management
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import desc

from app import db
from app.models.note import Note

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/notes')
@login_required
def notes():
    """Notes page"""
    # Get filter parameters
    tag_filter = request.args.get('tag')
    color_filter = request.args.get('color')
    sort_by = request.args.get('sort', 'updated')  # default to updated_at

    # Base query
    query = Note.query.filter_by(user_id=current_user.id)

    # Apply filters
    if tag_filter:
        query = query.filter(Note.tags.like(f"%{tag_filter}%"))
    if color_filter:
        query = query.filter_by(color=color_filter)

    # Apply sorting
    if sort_by == 'created':
        query = query.order_by(desc(Note.created_at))
    elif sort_by == 'updated':
        query = query.order_by(desc(Note.updated_at))
    elif sort_by == 'pinned':
        query = query.order_by(desc(Note.is_pinned), desc(Note.updated_at))
    else:
        # Default to position on board
        query = query.order_by(desc(Note.z_index))

    # Get all notes for the current user
    notes = query.all()

    # Get unique tags for filter dropdown
    all_tags = set()
    for note in notes:
        if note.tags:
            all_tags.update(note.tag_list)

    # Get unique colors for filter dropdown
    colors = db.session.query(Note.color).filter_by(user_id=current_user.id).distinct().all()
    colors = [color[0] for color in colors]

    return render_template('notes/notes.html',
                           title='Notes',
                           notes=notes,
                           tags=sorted(all_tags),
                           colors=colors,
                           current_tag=tag_filter,
                           current_color=color_filter,
                           current_sort=sort_by)


@notes_bp.route('/notes/create', methods=['POST'])
@login_required
def create_note():
    """Create a new note"""
    if request.is_json:
        # For AJAX requests
        data = request.json
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        color = data.get('color', '#fff740')
        position_x = data.get('position_x', 0)
        position_y = data.get('position_y', 0)
        tags = data.get('tags', '')
        is_pinned = data.get('is_pinned', False)
    else:
        # For form submissions
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        color = request.form.get('color', '#fff740')
        position_x = request.form.get('position_x', 0, type=int)
        position_y = request.form.get('position_y', 0, type=int)
        tags = request.form.get('tags', '')
        is_pinned = request.form.get('is_pinned', False, type=bool)

    if not content:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Note content cannot be empty'}), 400
        flash('Note content cannot be empty', 'danger')
        return redirect(url_for('notes.notes'))

    # If position is not provided or is 0, set to center (with small random offset)
    if position_x == 0 and position_y == 0:
        import random
        # Assume reasonable board dimensions
        position_x = 300 + random.randint(-30, 30)  # Center with slight randomness
        position_y = 200 + random.randint(-30, 30)

    # Get highest z-index
    highest_z = db.session.query(db.func.max(Note.z_index)).filter_by(user_id=current_user.id).scalar() or 0

    note = Note(
        title=title if title else None,
        content=content,
        user_id=current_user.id,
        color=color,
        position_x=position_x,
        position_y=position_y,
        tags=tags,
        is_pinned=is_pinned
    )
    note.z_index = highest_z + 1  # Put on top

    db.session.add(note)
    db.session.commit()

    if request.is_json:
        return jsonify({'success': True, 'note': note.to_dict()})

    flash('Note created successfully!', 'success')
    return redirect(url_for('notes.notes'))


@notes_bp.route('/notes/<int:note_id>/update', methods=['POST'])
@login_required
def update_note(note_id):
    """Update an existing note"""
    # Get the note data from the request
    data = request.json
    title = data.get('title')
    content = data.get('content')
    color = data.get('color')
    position_x = data.get('position_x')
    position_y = data.get('position_y')
    z_index = data.get('z_index')
    is_pinned = data.get('is_pinned')
    tags = data.get('tags')

    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()

    # Update note fields
    if title is not None:
        note.title = title if title.strip() else None
    if content is not None:
        note.content = content
    if color is not None:
        note.color = color
    if position_x is not None:
        note.position_x = position_x
    if position_y is not None:
        note.position_y = position_y
    if z_index is not None:
        note.z_index = z_index
    if is_pinned is not None:
        note.is_pinned = is_pinned
    if tags is not None:
        note.tags = tags

    db.session.commit()

    return jsonify({'success': True, 'note': note.to_dict()})


@notes_bp.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    """Delete a note"""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()

    db.session.delete(note)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    flash('Note deleted successfully!', 'success')
    return redirect(url_for('notes.notes'))


@notes_bp.route('/notes/<int:note_id>/toggle_pin', methods=['POST'])
@login_required
def toggle_pin(note_id):
    """Toggle the pinned status of a note"""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()

    note.is_pinned = not note.is_pinned
    db.session.commit()

    return jsonify({'success': True, 'is_pinned': note.is_pinned})


@notes_bp.route('/notes/bring_to_front/<int:note_id>', methods=['POST'])
@login_required
def bring_to_front(note_id):
    """Bring a note to the front"""
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()

    # Get highest z-index
    highest_z = db.session.query(db.func.max(Note.z_index)).filter_by(user_id=current_user.id).scalar() or 0

    note.z_index = highest_z + 1
    db.session.commit()

    return jsonify({'success': True, 'z_index': note.z_index})