from datetime import datetime
from app import db


class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)  # New field for soft deletion
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=0)  # 0: Low, 1: Medium, 2: High
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # New field to track deletion time
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.title}>'

    def soft_delete(self):
        """Soft delete a todo item instead of removing from the database"""
        self.deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore a soft-deleted todo item"""
        self.deleted = False
        self.deleted_at = None