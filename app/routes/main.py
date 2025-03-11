"""
Main routes for the application
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/home")
def home():
    """
    Home page route
    If user is not authenticated, redirect to login page
    """
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    return render_template("index.html", title="Home")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard route - requires authentication"""
    return render_template("dashboard.html", title="Dashboard")