# app/models/game.py
"""
Game model for storing game information
"""
from datetime import datetime
from app import db


class Game(db.Model):
    """
    Game model for storing games and user scores

    Attributes:
        id (int): Primary key
        title (str): Game title
        description (str): Game description
        game_type (str): Type of game (puzzle, arcade, etc.)
        difficulty (str): Game difficulty level
        created_at (datetime): Game creation timestamp
        updated_at (datetime): Game last update timestamp
        active (bool): Whether the game is active
    """
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    game_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    # Relationships
    scores = db.relationship('GameScore', backref='game', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, title, game_type, description=None, difficulty=None,
                 instructions=None, thumbnail=None, active=True):
        self.title = title
        self.game_type = game_type
        self.description = description
        self.difficulty = difficulty
        self.instructions = instructions
        self.thumbnail = thumbnail
        self.active = active

    def __repr__(self):
        return f"<Game {self.id}: {self.title}>"

    def to_dict(self):
        """Convert game to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'game_type': self.game_type,
            'difficulty': self.difficulty,
            'instructions': self.instructions,
            'thumbnail': self.thumbnail,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'active': self.active
        }