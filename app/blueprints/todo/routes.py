from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Todo
from app.blueprints.todo import todo_bp
from app.blueprints.todo.forms import TodoForm, TodoStatusForm
from datetime import datetime


@todo_bp.route('/')
@login_required
def list_todos():
    # Get the active tab from the query parameter, default to 'pending'
    active_tab = request.args.get('tab', 'pending')

    # Add this line to create a form for the checkboxes
    status_form = TodoStatusForm()

    # Filter todos based on the active tab
    if active_tab == 'completed':
        todos = Todo.query.filter_by(
            user_id=current_user.id,
            completed=True,
            deleted=False
        ).order_by(Todo.due_date.asc(), Todo.priority.desc()).all()
    elif active_tab == 'deleted':
        todos = Todo.query.filter_by(
            user_id=current_user.id,
            deleted=True
        ).order_by(Todo.deleted_at.desc()).all()
    else:  # pending tab (default)
        todos = Todo.query.filter_by(
            user_id=current_user.id,
            completed=False,
            deleted=False
        ).order_by(Todo.due_date.asc(), Todo.priority.desc()).all()

    # Get counts for each tab
    pending_count = Todo.query.filter_by(user_id=current_user.id, completed=False, deleted=False).count()
    completed_count = Todo.query.filter_by(user_id=current_user.id, completed=True, deleted=False).count()
    deleted_count = Todo.query.filter_by(user_id=current_user.id, deleted=True).count()

    return render_template(
        'todo/list.html',
        title='My Tasks',
        todos=todos,
        active_tab=active_tab,
        pending_count=pending_count,
        completed_count=completed_count,
        deleted_count=deleted_count,
        form=status_form  # Add this line to pass the form to the template
    )


@todo_bp.route('/new', methods=['POST'])
@login_required
def new_todo():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        priority = int(request.form.get('priority', 0))
        due_date_str = request.form.get('due_date')

        due_date = None
        if due_date_str and due_date_str.strip():
            due_date = datetime.fromisoformat(due_date_str)

        todo = Todo(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            user_id=current_user.id
        )
        db.session.add(todo)
        db.session.commit()
        flash('Task created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating task: {str(e)}', 'danger')

    # Always redirect back to the todo list
    return redirect(url_for('todo.list_todos'))


@todo_bp.route('/<int:todo_id>/update-status', methods=['POST'])
@login_required
def update_status(todo_id):
    todo = Todo.query.get_or_404(todo_id)

    # Ensure the current user owns this todo
    if todo.user_id != current_user.id:
        abort(403)

    # Update the completed status
    completed = 'completed' in request.form
    todo.completed = completed
    db.session.commit()

    # Flash message based on the new status
    if completed:
        flash('Task marked as completed!', 'success')
    else:
        flash('Task marked as pending!', 'info')

    # Redirect to referer or default to todo list
    next_page = request.args.get('next') or request.referrer
    if not next_page:
        next_page = url_for('todo.list_todos')
    return redirect(next_page)


@todo_bp.route('/<int:todo_id>/edit', methods=['POST'])
@login_required
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)

    # Ensure the current user owns this todo
    if todo.user_id != current_user.id:
        abort(403)

    # Prevent editing deleted tasks
    if todo.deleted:
        flash('Cannot edit a deleted task. Restore it first.', 'warning')
        return redirect(url_for('todo.list_todos', tab='deleted'))

    try:
        todo.title = request.form.get('title')
        todo.description = request.form.get('description')
        todo.priority = int(request.form.get('priority', 0))

        due_date_str = request.form.get('due_date')
        if due_date_str and due_date_str.strip():
            todo.due_date = datetime.fromisoformat(due_date_str)
        else:
            todo.due_date = None

        db.session.commit()
        flash('Task updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task: {str(e)}', 'danger')

    # Redirect to referer or default to todo list
    next_page = request.args.get('next') or request.referrer
    if not next_page:
        next_page = url_for('todo.list_todos')
    return redirect(next_page)


@todo_bp.route('/<int:todo_id>/delete', methods=['POST'])
@login_required
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)

    # Ensure the current user owns this todo
    if todo.user_id != current_user.id:
        abort(403)

    # Instead of hard delete, use soft delete
    todo.soft_delete()
    db.session.commit()
    flash('Task moved to trash.', 'success')

    # Redirect to the appropriate tab
    return redirect(url_for('todo.list_todos', tab=request.args.get('tab', 'pending')))


@todo_bp.route('/<int:todo_id>/restore', methods=['POST'])
@login_required
def restore_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)

    # Ensure the current user owns this todo
    if todo.user_id != current_user.id:
        abort(403)

    # Restore the todo
    todo.restore()
    db.session.commit()
    flash('Task restored successfully!', 'success')

    # Redirect to the deleted tab
    return redirect(url_for('todo.list_todos', tab='deleted'))


@todo_bp.route('/<int:todo_id>/permanent-delete', methods=['POST'])
@login_required
def permanent_delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)

    # Ensure the current user owns this todo
    if todo.user_id != current_user.id:
        abort(403)

    # Permanently delete the todo
    db.session.delete(todo)
    db.session.commit()
    flash('Task permanently deleted.', 'success')

    # Redirect to the deleted tab
    return redirect(url_for('todo.list_todos', tab='deleted'))