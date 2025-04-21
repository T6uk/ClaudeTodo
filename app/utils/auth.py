"""
Authentication utilities for the todo application
"""
from flask import request, render_template, redirect, url_for, session, flash, current_app
from functools import wraps

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function