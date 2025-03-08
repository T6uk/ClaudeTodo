from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()


def create_app(config_class=Config):
    # Initialize application
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.todo import todo_bp
    from app.blueprints.calendar import calendar_bp
    from app.blueprints.challenges import challenges_bp
    from app.blueprints.workout import workout_bp
    from app.blueprints.health import health_bp
    from app.blueprints.games import games_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(todo_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(challenges_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(games_bp)

    # Create a route for the home page
    @app.route('/')
    def home():
        from flask import render_template
        return render_template('home.html')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app