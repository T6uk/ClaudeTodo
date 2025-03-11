"""
Authentication routes for login, logout, and registration
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from app import db
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login route"""
    # Redirect if user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            # Log in user and update last login timestamp
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()

            # Redirect to requested page or default to home
            next_page = request.args.get("next")
            flash("Login successful!", "success")
            return redirect(next_page or url_for("main.home"))
        else:
            flash("Login failed. Please check your email and password.", "danger")

    return render_template("auth/login.html", title="Login", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration route"""
    # Redirect if user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )

        # Add user to database
        db.session.add(user)
        db.session.commit()

        flash("Your account has been created! You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", title="Register", form=form)


@auth_bp.route("/profile")
@login_required
def profile():
    """User profile route"""
    return render_template("auth/profile.html", title="Profile")