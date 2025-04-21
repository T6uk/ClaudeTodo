"""
Todo model for task management
"""
from datetime import datetime
from app import db


class Todo(db.Model):
    """
    Todo model for task management

    Attributes:
        id (int): Primary key
        title (str): Task title
        description (str): Task description
        due_date (datetime): Task due date
        priority (str): Task priority (low, medium, high)
        created_at (datetime): Task creation timestamp
        updated_at (datetime): Task last update timestamp
        creator_id (int): User ID of task creator
        assignee_id (int): User ID of task assignee
    """
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id], backref=db.backref('created_todos', lazy='dynamic'))
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref=db.backref('assigned_todos', lazy='dynamic'))

    def __init__(self, title, creator_id, assignee_id, description=None, due_date=None, priority='medium'):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.creator_id = creator_id
        self.assignee_id = assignee_id

    def __repr__(self):
        return f"<Todo {self.id}: {self.title}>"

    def to_dict(self):
        """Convert todo to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'creator_id': self.creator_id,
            'creator_name': self.creator.username,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee.username
        }