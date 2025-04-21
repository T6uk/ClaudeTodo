"""
Simplified User model for the todo application
"""
from app import db


class User(db.Model):
    """
    User model for the todo application

    Attributes:
        id (int): Primary key
        username (str): User's username
        full_name (str): User's full name
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)

    def __init__(self, username, full_name):
        self.username = username
        self.full_name = full_name

    def __repr__(self):
        return f"<User {self.username}>"