# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from datetime import datetime

# Create extensions instances first, before any imports that might use them
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = config_class.PERMANENT_SESSION_LIFETIME

    db.init_app(app)
    migrate.init_app(app, db)

    # Register custom template filters
    @app.template_filter('now')
    def filter_now(format_string):
        if format_string == 'year':
            return datetime.now().year
        return datetime.now()

    @app.template_filter('datetime')
    def filter_datetime(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now()

    # Import and register blueprints
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Create database tables
    with app.app_context():
        db.create_all()
        # Import models inside app context to avoid circular imports
        from app.models import User, Category, Tag

        # Create default users if they don't exist
        if User.query.count() == 0:
            user1 = User(name='Romet', avatar_color='blue', email='romet@example.com')
            user2 = User(name='Eliis', avatar_color='purple', email='eliis@example.com')
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

        # Create default categories if they don't exist
        if Category.query.count() == 0:
            categories = [
                Category(name='Töö', color='blue'),
                Category(name='Isiklik', color='green'),
                Category(name='Tervis', color='red'),
                Category(name='Haridus', color='purple'),
                Category(name='Asjatoimetused', color='yellow')
            ]
            db.session.add_all(categories)
            db.session.commit()

    return app