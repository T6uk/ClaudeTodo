import os
import secrets
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///todo_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_PASSWORD = os.environ.get('APP_PASSWORD') or '1234'  # Set a default password for the app
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)  # Session will last 30 days