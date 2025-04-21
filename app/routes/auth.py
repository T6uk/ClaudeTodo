"""
Authentication routes for the todo application
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""
    # If already logged in, redirect to todos
    if session.get('logged_in'):
        return redirect(url_for('todo.todos'))

    # Handle login form submission
    if request.method == "POST":
        password = request.form.get('password')

        # Check password - in a real app, you'd use a secure password hash
        if password == 'todoapp2025':  # Simple password for demonstration
            session['logged_in'] = True

            # Default to first user
            if not session.get('user_id'):
                first_user = User.query.first()
                if first_user:
                    session['user_id'] = first_user.id

            flash('Login successful!', 'success')

            # Redirect to the original page or todos
            next_page = request.args.get('next')
            return redirect(next_page or url_for('todo.todos'))
        else:
            flash('Incorrect password!', 'danger')

    return render_template('auth/login.html', title='Login')


@auth_bp.route("/logout")
def logout():
    """Logout route"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))