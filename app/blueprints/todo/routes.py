from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from app import db
from app.models import Todo
from app.blueprints.todo import todo_bp
from app.blueprints.todo.forms import TodoForm, TodoStatusForm


@todo_bp.route('/')
@login_required
def list_todos():
    todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.due_date.asc(), Todo.priority.desc()).all()
    return render_template('todo/list.html', title='My Tasks', todos=todos)


@todo_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_todo():
    form = TodoForm()
    if form.validate_on_submit():
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

    return render_template('todo/item.html', title='New Task', form=form, is_update=False)


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

    form = TodoForm()

    if form.validate_on_submit():
        todo.title = form.title.data
        todo.description = form.description.data
        todo.priority = form.priority.data
        todo.due_date = form.due_date.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('todo.view_todo', todo_id=todo.id))

    # Pre-fill the form with current data
    if request.method == 'GET':
        form.title.data = todo.title
        form.description.data = todo.description
        form.priority.data = todo.priority
        form.due_date.data = todo.due_date

    return render_template('todo/item.html', title='Edit Task', form=form, is_update=True)


@todo_bp.route('/<int:todo_id>/delete', methods=['POST'])
@login_required
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)

    # Ensure the current user owns this todo
    if todo.user_id != current_user.id:
        abort(403)

    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('todo.list_todos'))