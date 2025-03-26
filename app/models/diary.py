"""
Enhanced Diary model for personal journal entries
"""
from datetime import datetime
import json
from app import db


class DiaryEntry(db.Model):
    """
    DiaryEntry model for storing personal journal entries

    Attributes:
        id (int): Primary key
        title (str): Entry title
        content (text): Entry content/body
        mood (str): User's mood when writing
        category (str): Optional category for organization
        tags (str): JSON string of tags for the entry
        is_favorite (bool): Whether entry is marked as favorite
        is_private (bool): Whether entry is marked as private/sensitive
        weather (str): Optional weather information
        location (str): Optional location information
        sentiment_score (float): Calculated sentiment score (-1 to 1)
        word_count (int): Number of words in the entry
        created_at (datetime): Entry creation timestamp
        updated_at (datetime): Entry last update timestamp
        user_id (int): User ID who owns the entry
    """
    __tablename__ = 'diary_entries'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    tags = db.Column(db.Text, nullable=True)  # Stored as JSON string
    is_favorite = db.Column(db.Boolean, default=False)
    is_private = db.Column(db.Boolean, default=False)
    weather = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    sentiment_score = db.Column(db.Float, nullable=True)
    word_count = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('diary_entries', lazy='dynamic', cascade='all, delete-orphan'))

    def __init__(self, title, content, user_id, mood=None, category=None,
                 tags=None, is_favorite=False, is_private=False,
                 weather=None, location=None):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.mood = mood
        self.category = category
        self.set_tags(tags or [])
        self.is_favorite = is_favorite
        self.is_private = is_private
        self.weather = weather
        self.location = location
        self.update_word_count()

    def __repr__(self):
        return f"<DiaryEntry {self.id}: {self.title}>"

    def update_word_count(self):
        """Update the word count of the entry"""
        if self.content:
            self.word_count = len(self.content.split())
        else:
            self.word_count = 0

    def set_tags(self, tags_list):
        """Set tags from a list"""
        if isinstance(tags_list, list):
            self.tags = json.dumps(tags_list)
        elif isinstance(tags_list, str):
            # If it's already a JSON string, store it directly
            try:
                json.loads(tags_list)  # Validate JSON
                self.tags = tags_list
            except json.JSONDecodeError:
                # If not valid JSON, treat as a comma-separated string
                tags = [tag.strip() for tag in tags_list.split(',') if tag.strip()]
                self.tags = json.dumps(tags)
        else:
            self.tags = json.dumps([])

    def get_tags(self):
        """Get tags as a list"""
        if not self.tags:
            return []

        try:
            return json.loads(self.tags)
        except json.JSONDecodeError:
            return []

    def to_dict(self):
        """Convert diary entry to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'mood': self.mood,
            'category': self.category,
            'tags': self.get_tags(),
            'is_favorite': self.is_favorite,
            'is_private': self.is_private,
            'weather': self.weather,
            'location': self.location,
            'sentiment_score': self.sentiment_score,
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }