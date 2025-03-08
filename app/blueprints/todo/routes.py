from flask import render_template, redirect, url_for, flash, request, abort
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
        deleted_count=deleted_count
    )


@todo_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_todo():
    form = TodoForm()
    if form.validate_on_submit():
        try:
            todo = Todo(
                title=form.title.data,
                description=form.description.data,
                priority=form.priority.data,
                due_date=form.due_date.data,
                user_id=current_user.id
            )
            db.session.add(todo)
            db.session.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('todo.list_todos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating task: {str(e)}', 'danger')
            return render_template('todo/item.html', title='New Task', form=form, is_update=False, todo=None)

    return render_template('todo/item.html', title='New Task', form=form, is_update=False, todo=None)


@todo_bp.route('/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def view_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)

    # Ensure the current user owns this todo
    if todo.user_id != current_user.id:
        abort(403)

    status_form = TodoStatusForm()

    if status_form.validate_on_submit():
        todo.completed = status_form.completed.data
        db.session.commit()
        flash('Task status updated!', 'success')
        return redirect(url_for('todo.view_todo', todo_id=todo.id))

    # Pre-fill the form with current data
    if request.method == 'GET':
        status_form.completed.data = todo.completed

    return render_template('todo/view.html', title=todo.title, todo=todo, form=status_form)


@todo_bp.route('/<int:todo_id>/edit', methods=['GET', 'POST'])
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

    form = TodoForm()

    if form.validate_on_submit():
        try:
            todo.title = form.title.data
            todo.description = form.description.data
            todo.priority = form.priority.data
            todo.due_date = form.due_date.data
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('todo.view_todo', todo_id=todo.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating task: {str(e)}', 'danger')

    # Pre-fill the form with current data
    if request.method == 'GET':
        form.title.data = todo.title
        form.description.data = todo.description
        form.priority.data = todo.priority
        form.due_date.data = todo.due_date

    return render_template('todo/item.html', title='Edit Task', form=form, is_update=True, todo=todo)


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