# app/models/game.py
"""
Expanded Game model for storing game information and providing more details
"""
from datetime import datetime
from app import db


class Game(db.Model):
    """
    Enhanced Game model with additional attributes and relationships
    """
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    game_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(200), nullable=True)

    # Game configuration options
    max_players = db.Column(db.Integer, default=1)
    multiplayer_support = db.Column(db.Boolean, default=False)
    global_leaderboard = db.Column(db.Boolean, default=True)
    weekly_reset = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

    # Relationships
    scores = db.relationship('GameScore', backref='game', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, title, game_type, description=None, difficulty=None,
                 instructions=None, thumbnail=None, max_players=1,
                 multiplayer_support=False, global_leaderboard=True,
                 weekly_reset=False, active=True):
        self.title = title
        self.game_type = game_type
        self.description = description
        self.difficulty = difficulty
        self.instructions = instructions
        self.thumbnail = thumbnail
        self.max_players = max_players
        self.multiplayer_support = multiplayer_support
        self.global_leaderboard = global_leaderboard
        self.weekly_reset = weekly_reset
        self.active = active

    def to_dict(self):
        """Convert game to dictionary with more details"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'game_type': self.game_type,
            'difficulty': self.difficulty,
            'instructions': self.instructions,
            'thumbnail': self.thumbnail,
            'max_players': self.max_players,
            'multiplayer_support': self.multiplayer_support,
            'global_leaderboard': self.global_leaderboard,
            'weekly_reset': self.weekly_reset,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'active': self.active
        }