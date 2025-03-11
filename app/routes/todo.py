"""
Todo routes for task management
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime

from app import db
from app.models.user import User
from app.models.todo import Todo
from app.forms.todo_forms import TodoForm

todo_bp = Blueprint("todo", __name__)


@todo_bp.route("/todos")
@login_required
def todos():
    """Todo list page"""
    todos = Todo.query.all()
    form = TodoForm()

    # Set up user choices for assignee field
    users = User.query.all()
    form.assignees.choices = [(u.id, u.username) for u in users]

    return render_template("todo/todos.html",
                           title="Todo List",
                           todos=todos,
                           form=form)


@todo_bp.route("/todos/create", methods=["POST"])
@login_required
def create_todo():
    """Create a new todo"""
    form = TodoForm()

    # Set up user choices for assignee field
    users = User.query.all()
    form.assignees.choices = [(u.id, u.username) for u in users]

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
            priority=int(form.priority.data),
            creator_id=current_user.id
        )

        # Add assignees
        if form.assignees.data:
            assignee_users = User.query.filter(User.id.in_(form.assignees.data)).all()
            todo.assignees = assignee_users

        # Add to database
        db.session.add(todo)
        db.session.commit()

        flash("Task created successfully!", "success")
        return redirect(url_for("todo.todos"))

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
    form = TodoForm()

    # Set up user choices for assignee field
    users = User.query.all()
    form.assignees.choices = [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        # Update todo fields
        todo.title = form.title.data
        todo.description = form.description.data
        todo.priority = int(form.priority.data)
        todo.completed = form.completed.data

        # Convert due date from string to datetime if provided
        if form.due_date.data:
            todo.due_date = form.due_date.data
        else:
            todo.due_date = None

        # Update assignees
        if form.assignees.data:
            assignee_users = User.query.filter(User.id.in_(form.assignees.data)).all()
            todo.assignees = assignee_users
        else:
            todo.assignees = []

        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for("todo.todos"))

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


@todo_bp.route("/todos/<int:todo_id>/toggle", methods=["POST"])
@login_required
def toggle_todo(todo_id):
    """Toggle todo completion status"""
    todo = Todo.query.get_or_404(todo_id)

    todo.completed = not todo.completed
    db.session.commit()

    status = "completed" if todo.completed else "pending"
    flash(f"Task marked as {status}!", "success")
    return redirect(url_for("todo.todos"))