"""
Initialize the Flask application
"""
import os
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from app.config import config_dict

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
login_manager.login_message = "Please log in to access this page."


def create_app(config_name=None):
    """
    Application factory function

    Args:
        config_name (str): Configuration environment name

    Returns:
        Flask app instance
    """
    # Initialize the Flask application
    app = Flask(__name__)

    # Get configuration
    config_name = config_name or os.environ.get("FLASK_ENV", "default")
    app.config.from_object(config_dict[config_name])

    # Configure remember cookie
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
    app.config["REMEMBER_COOKIE_SECURE"] = False  # Set to True in production with HTTPS
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_REFRESH_EACH_REQUEST"] = True

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @app.template_filter('abs')
    def abs_filter(n):
        """Absolute value filter for templates"""
        return abs(n)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.todo import todo_bp
    from app.routes.calendar import calendar_bp
    from app.routes.challenge import challenge_bp
    from app.routes.health import health_bp
    from app.routes.games import games_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.diary import diary_bp  # Add this line
    from app.utils.markdown_filter import setup_markdown_filter

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(todo_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(challenge_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(diary_bp)  # Add this line
    setup_markdown_filter(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """Register error handlers"""
    from flask import render_template

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500