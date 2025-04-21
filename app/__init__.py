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

    db.init_app(app)
    migrate.init_app(app, db)

    # Register custom template filters
    @app.template_filter('now')
    def filter_now(format_string):
        if format_string == 'year':
            return datetime.now().year
        return datetime.now()

    # Import and register blueprints
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Create database tables
    with app.app_context():
        db.create_all()
        # Import models inside app context to avoid circular imports
        from app.models import User
        # Create default users if they don't exist
        if User.query.count() == 0:
            user1 = User(name='Romet')
            user2 = User(name='Eliis')
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

    return app