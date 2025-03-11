"""
GameScore model for tracking user game scores
"""
from datetime import datetime
from app import db


class GameScore(db.Model):
    """
    GameScore model for tracking user game scores

    Attributes:
        id (int): Primary key
        score (int): User's score
        date (datetime): When the score was achieved
        user_id (int): User ID who achieved the score
        game_id (int): Game ID the score is for
    """
    __tablename__ = 'game_scores'

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('game_scores', lazy='dynamic'))

    def __init__(self, user_id, game_id, score):
        self.user_id = user_id
        self.game_id = game_id
        self.score = score

    def __repr__(self):
        return f"<GameScore {self.id}: {self.score} - User {self.user_id} - Game {self.game_id}>"

    def to_dict(self):
        """Convert score to dictionary"""
        return {
            'id': self.id,
            'score': self.score,
            'date': self.date.isoformat() if self.date else None,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'game_id': self.game_id,
            'game_title': self.game.title if self.game else None
        }