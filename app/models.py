# app/models.py
from datetime import datetime
# Import db directly from the module where it's defined
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    avatar_color = db.Column(db.String(20), default='blue')
    todos = db.relationship('Todo', backref='assigned_to', lazy='dynamic',
                            foreign_keys='Todo.user_id')
    created_todos = db.relationship('Todo', backref='creator', lazy='dynamic',
                                    foreign_keys='Todo.created_by_id')
    events = db.relationship('Event', backref='creator', lazy='dynamic',
                             foreign_keys='Event.created_by_id')

    def __repr__(self):
        return f'<User {self.name}>'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='blue')
    todos = db.relationship('Todo', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    priority = db.Column(db.String(20), nullable=False)  # low, medium, high
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)  # Added deleted field for soft delete
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    tags = db.relationship('Tag', secondary='todo_tags', backref='todos')

    def __repr__(self):
        return f'<Todo {self.title}>'


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)

    def __repr__(self):
        return f'<Tag {self.name}>'


# Association table for many-to-many relationship between Todo and Tag
todo_tags = db.Table('todo_tags',
                     db.Column('todo_id', db.Integer, db.ForeignKey('todo.id'), primary_key=True),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                     )


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    all_day = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(20), default='blue')  # For event styling
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Event {self.title}>'