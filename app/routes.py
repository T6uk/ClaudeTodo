from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from app import db
from app.models import Todo, User
from datetime import datetime
from functools import wraps

bp = Blueprint('main', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == current_app.config['APP_PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password', 'danger')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.login'))


@bp.route('/')
@login_required
def index():
    todos = Todo.query.order_by(Todo.due_date).all()
    users = User.query.all()
    return render_template('index.html', todos=todos, users=users)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_todo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        user_id = int(request.form.get('user_id'))
        created_by_id = int(request.form.get('created_by_id'))
        priority = request.form.get('priority')

        todo = Todo(
            title=title,
            description=description,
            due_date=due_date,
            user_id=user_id,
            created_by_id=created_by_id,
            priority=priority
        )

        db.session.add(todo)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('create_todo.html', users=users)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_todo(id):
    todo = Todo.query.get_or_404(id)

    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        todo.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        todo.user_id = int(request.form.get('user_id'))
        todo.priority = request.form.get('priority')
        todo.completed = 'completed' in request.form

        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.index'))

    users = User.query.all()
    # Format date for the datetime-local input
    formatted_date = todo.due_date.strftime('%Y-%m-%dT%H:%M')
    return render_template('edit_todo.html', todo=todo, users=users, formatted_date=formatted_date)


@bp.route('/delete/<int:id>')
@login_required
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.index'))


@bp.route('/toggle_complete/<int:id>')
@login_required
def toggle_complete(id):
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    status = "completed" if todo.completed else "marked as active"
    flash(f'Task {status}!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/events')
@login_required
def events():
    # This is a placeholder for the Events feature
    return render_template('events.html')