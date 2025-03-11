"""
Todo model for task management
"""
from datetime import datetime
from app import db
from sqlalchemy.ext.associationproxy import association_proxy

# Association table for many-to-many relationship between todos and users
todo_assignees = db.Table('todo_assignees',
    db.Column('todo_id', db.Integer, db.ForeignKey('todos.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Todo(db.Model):
    """
    Todo model for task management

    Attributes:
        id (int): Primary key
        title (str): Task title
        description (str): Task description
        due_date (datetime): Task due date
        priority (int): Task priority (1-5 scale, 5 being highest)
        completed (bool): Task completion status
        created_at (datetime): Task creation timestamp
        updated_at (datetime): Task last update timestamp
        creator_id (int): User ID of task creator
        assignees (list): Users assigned to this task
    """
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=3)  # 1-5 scale
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id], backref=db.backref('created_todos', lazy='dynamic'))
    assignees = db.relationship('User', secondary=todo_assignees, backref=db.backref('assigned_todos', lazy='dynamic'))

    def __init__(self, title, creator_id, description=None, due_date=None, priority=3):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.creator_id = creator_id

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
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'creator_id': self.creator_id,
            'creator_name': self.creator.username,
            'assignees': [{'id': user.id, 'username': user.username} for user in self.assignees]
        }