import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Secret key for signing cookies and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-key-change-in-production'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///personal_dashboard.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False