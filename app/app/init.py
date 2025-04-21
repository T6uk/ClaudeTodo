"""
Initialize the Flask application
"""
import os
from datetime import timedelta
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config import config_dict

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


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

    # Set up session configuration
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)
    app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production with HTTPS
    app.config["SESSION_COOKIE_HTTPONLY"] = True

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    @app.template_filter('abs')
    def abs_filter(n):
        """Absolute value filter for templates"""
        return abs(n)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.todo import todo_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(todo_bp)

    # Register error handlers
    register_error_handlers(app)

    # Initialize database
    with app.app_context():
        init_db()

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


def init_db():
    """Initialize database with required data"""
    from app.models.user import User

    # Create tables
    db.create_all()

    # Check if users already exist
    romet = User.query.filter_by(username='Romet').first()
    eliis = User.query.filter_by(username='Eliis').first()

    # Create users if they don't exist
    if not romet:
        romet = User(username='Romet', full_name='Romet')
        db.session.add(romet)

    if not eliis:
        eliis = User(username='Eliis', full_name='Eliis')
        db.session.add(eliis)

    db.session.commit()