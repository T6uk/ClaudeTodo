"""
Note model for quick sticky notes
"""
from datetime import datetime
from app import db
from flask_login import current_user


class Note(db.Model):
    """
    Note model for quick sticky notes

    Attributes:
        id (int): Primary key
        title (str): Optional note title
        content (str): Note content
        color (str): Note color (hex code or name)
        position_x (int): X coordinate on the board
        position_y (int): Y coordinate on the board
        z_index (int): Z-index for stacking notes
        is_pinned (bool): Whether the note is pinned to the top
        tags (str): Comma-separated tags for the note
        created_at (datetime): Note creation timestamp
        updated_at (datetime): Note last update timestamp
        user_id (int): User ID of note creator
    """
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(20), default='#fff740')  # Default yellow
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    z_index = db.Column(db.Integer, default=1)
    is_pinned = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('notes', lazy='dynamic'))

    def __init__(self, content, user_id, title=None, color='#fff740', position_x=0, position_y=0, tags=None, is_pinned=False):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.color = color
        self.position_x = position_x
        self.position_y = position_y
        self.tags = tags
        self.is_pinned = is_pinned

    def __repr__(self):
        return f"<Note {self.id}: {self.content[:20]}...>"

    def to_dict(self):
        """Convert note to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'color': self.color,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'z_index': self.z_index,
            'is_pinned': self.is_pinned,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        }

    @property
    def tag_list(self):
        """Return a list of tags"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]