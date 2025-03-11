# Personal Website

A personal website built with Flask, featuring a user authentication system.

## Features

- User authentication (register, login, logout)
- User profile management
- Responsive design with Bootstrap 5
- SQLAlchemy ORM integration
- Flask-Login for session management

## Project Structure

```
PersonalWebSite/
│
├── app/                      # Main application package
│   ├── __init__.py           # App initialization and factory
│   ├── config.py             # Configuration settings
│   ├── models/               # SQLAlchemy data models
│   │   ├── __init__.py
│   │   └── user.py           # User model
│   ├── routes/               # Route definitions
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication routes
│   │   └── main.py           # Main routes
│   ├── forms/                # WTForms forms
│   │   ├── __init__.py
│   │   └── auth_forms.py     # Authentication forms
│   ├── static/               # Static assets
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   └── templates/            # Jinja2 templates
│       ├── base.html         # Base template
│       ├── index.html        # Home page
│       ├── dashboard.html    # User dashboard
│       ├── auth/             # Authentication templates
│       │   ├── login.html
│       │   ├── register.html
│       │   └── profile.html
│       └── errors/           # Error pages
│           ├── 404.html
│           └── 500.html
│
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
├── README.md                 # Project README
├── requirements.txt          # Python dependencies
└── run.py                    # Application entry point
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/T6uk/PersonalWebSite.git
   cd PersonalWebSite
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with required environment variables (see `.env` example)

5. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application:
   ```
   python run.py
   ```

## Usage

- Access the application at `http://localhost:5000`
- Register a new account
- Log in with your credentials
- View your dashboard and profile

## Development

- Create database migrations when models change:
  ```
  flask db migrate -m "Description of changes"
  flask db upgrade
  ```

## License

This project is open-source and available under the MIT License.