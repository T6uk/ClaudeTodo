from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from app.config import Config
from datetime import datetime
import sqlite3

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()
csrf = CSRFProtect()


def create_app(config_class=Config):
    # Initialize application
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection properly

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

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Update database schema directly
    with app.app_context():
        try:
            # First try to create all tables (including any new models)
            db.create_all()

            # Then add new columns to existing tables if they don't exist
            database_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()

            # Check if the todos table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
            table_exists = cursor.fetchone() is not None

            if table_exists:
                # Check if the columns already exist
                cursor.execute("PRAGMA table_info(todos)")
                columns = [column[1] for column in cursor.fetchall()]

                # Add 'deleted' column if it doesn't exist
                if 'deleted' not in columns:
                    cursor.execute("ALTER TABLE todos ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT 0")
                    app.logger.info("Added 'deleted' column to todos table")

                # Add 'deleted_at' column if it doesn't exist
                if 'deleted_at' not in columns:
                    cursor.execute("ALTER TABLE todos ADD COLUMN deleted_at DATETIME")
                    app.logger.info("Added 'deleted_at' column to todos table")

            conn.commit()
            conn.close()
            app.logger.info("Database schema update check completed successfully.")

        except Exception as e:
            app.logger.error(f"Error updating database schema: {str(e)}")

    # Add a CLI command to update schema (can be useful in case of problems)
    @app.cli.command("update_todos_schema")
    def update_todos_schema():
        """Update the todos table schema to add deleted columns."""
        try:
            with app.app_context():
                db_uri = app.config['SQLALCHEMY_DATABASE_URI']
                if db_uri.startswith('sqlite:///'):
                    db_path = db_uri.replace('sqlite:///', '')

                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    # Check if the todos table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
                    table_exists = cursor.fetchone() is not None

                    if table_exists:
                        # Check if the columns already exist
                        cursor.execute("PRAGMA table_info(todos)")
                        columns = [column[1] for column in cursor.fetchall()]

                        # Add 'deleted' column if it doesn't exist
                        if 'deleted' not in columns:
                            cursor.execute("ALTER TABLE todos ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT 0")
                            print("Added 'deleted' column to todos table")

                        # Add 'deleted_at' column if it doesn't exist
                        if 'deleted_at' not in columns:
                            cursor.execute("ALTER TABLE todos ADD COLUMN deleted_at DATETIME")
                            print("Added 'deleted_at' column to todos table")

                        conn.commit()
                        print("Database schema updated successfully.")
                    else:
                        print("Todos table does not exist yet. It will be created with all columns by SQLAlchemy.")

                    conn.close()
        except Exception as e:
            print(f"Error updating database schema: {str(e)}")

    return app