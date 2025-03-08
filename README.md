# Personal Dashboard

A Flask-based personal dashboard web application that helps you stay organized, track your health, manage workouts, set challenges, and more.

## Features

- User authentication (register/login)
- Todo list management
- Calendar for scheduling events
- Challenges tracking with progress
- Workout tracking and exercise logging
- Health metrics monitoring
- Simple games for relaxation

## Project Structure

The project uses Flask blueprints for a modular, extensible structure:

- `auth`: User authentication and profile management
- `todo`: Task management functionality
- `calendar`: Event scheduling and calendar views
- `challenges`: Personal challenges with progress tracking
- `workout`: Workout logging and tracking
- `health`: Health metrics monitoring
- `games`: Simple browser games

## Setup and Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd personal-dashboard
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```
   # For development (Unix/Linux/Mac)
   export FLASK_APP=run.py
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key

   # For Windows
   set FLASK_APP=run.py
   set FLASK_ENV=development
   set SECRET_KEY=your-secret-key
   ```

   Alternatively, create a `.env` file with these settings.

5. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

7. Access the application at `http://localhost:5000`

## Extending the Application

The modular blueprint structure makes it easy to add new features:

1. Create a new blueprint directory in `app/blueprints/`
2. Define routes, forms, and templates for your feature
3. Register the blueprint in `app/__init__.py`

## Dependencies

- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Flask-Migrate: Database migrations
- Flask-Login: User authentication
- Flask-WTF: Form handling and validation
- Flask-Bcrypt: Password hashing
- Bootstrap 5: Frontend styling

## License

This project is licensed under the MIT License - see the LICENSE file for details.