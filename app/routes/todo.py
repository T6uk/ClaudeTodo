"""
Todo routes for task management
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, session, abort
from datetime import datetime

from app import db
from app.models.user import User
from app.models.todo import Todo
from app.forms.todo_forms import TodoForm
from app.utils.auth import login_required

todo_bp = Blueprint("todo", __name__)


@todo_bp.route("/")
@login_required
def index():
    """Redirect to todos page"""
    return redirect(url_for("todo.todos"))


@todo_bp.route("/todos")
@login_required
def todos():
    """Todo list page"""
    # Get all todos ordered by due date
    todos = Todo.query.order_by(Todo.due_date.asc()).all()

    # Get users for the form
    users = User.query.all()

    # Initialize form
    form = TodoForm()
    form.assignee.choices = [(u.id, u.username) for u in users]

    # Set current user
    current_user_id = session.get('user_id', 1)  # Default to first user
    current_user = User.query.get(current_user_id)

    return render_template("todo/todos.html",
                           title="Todo List",
                           todos=todos,
                           form=form,
                           current_user=current_user,
                           users=users)


@todo_bp.route("/todos/create", methods=["POST"])
@login_required
def create_todo():
    """Create a new todo"""
    # Get users for the form
    users = User.query.all()

    form = TodoForm()
    form.assignee.choices = [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        # Convert due date from string to datetime if provided
        due_date = None
        if form.due_date.data:
            due_date = form.due_date.data

        # Create new todo
        todo = Todo(
            title=form.title.data,
            description=form.description.data,
            due_date=due_date,
            priority=form.priority.data,
            creator_id=session.get('user_id', 1),  # Default to first user
            assignee_id=form.assignee.data
        )

        # Add to database
        db.session.add(todo)
        db.session.commit()

        flash("Task created successfully!", "success")
        return redirect(url_for("todo.todos"))

    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("todo.todos"))


@todo_bp.route("/todos/<int:todo_id>")
@login_required
def get_todo(todo_id):
    """Get todo details for modal"""
    todo = Todo.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())


@todo_bp.route("/todos/<int:todo_id>/update", methods=["POST"])
@login_required
def update_todo(todo_id):
    """Update an existing todo"""
    todo = Todo.query.get_or_404(todo_id)

    # Get users for the form
    users = User.query.all()

    form = TodoForm()
    form.assignee.choices = [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        # Update todo fields
        todo.title = form.title.data
        todo.description = form.description.data
        todo.priority = form.priority.data
        todo.assignee_id = form.assignee.data

        # Convert due date from string to datetime if provided
        if form.due_date.data:
            todo.due_date = form.due_date.data
        else:
            todo.due_date = None

        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for("todo.todos"))

    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("todo.todos"))


@todo_bp.route("/todos/<int:todo_id>/delete", methods=["POST"])
@login_required
def delete_todo(todo_id):
    """Delete a todo"""
    todo = Todo.query.get_or_404(todo_id)

    db.session.delete(todo)
    db.session.commit()

    flash("Task deleted successfully!", "success")
    return redirect(url_for("todo.todos"))


@todo_bp.route("/switch-user/<int:user_id>", methods=["GET"])
@login_required
def switch_user(user_id):
    """Switch current user"""
    user = User.query.get_or_404(user_id)
    session['user_id'] = user.id
    flash(f"Switched to user: {user.username}", "success")
    return redirect(url_for("todo.todos"))