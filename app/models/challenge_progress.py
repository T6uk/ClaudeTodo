"""
Challenge progress model for tracking user progress in challenges

This model provides a way to track individual user progress for each challenge.
Each participant in a challenge can have their own progress tracking entry.

"""
from datetime import datetime
from app import db


class ChallengeProgress(db.Model):
    """
    Challenge progress model for tracking user progress in challenges

    Attributes:
        id (int): Primary key
        user_id (int): User ID of the participant
        challenge_id (int): Challenge ID
        progress_value (float): Numerical progress value (e.g., percentage, count)
        target_value (float): Target goal value
        last_updated (datetime): Last update timestamp
        notes (str): Optional progress notes
    """
    __tablename__ = 'challenge_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    progress_value = db.Column(db.Float, default=0.0)
    target_value = db.Column(db.Float, default=100.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('challenge_progress', lazy='dynamic'))
    challenge = db.relationship('Challenge', foreign_keys=[challenge_id], backref=db.backref('progress_entries', lazy='dynamic'))

    def __init__(self, user_id, challenge_id, progress_value=0.0, target_value=100.0, notes=None):
        self.user_id = user_id
        self.challenge_id = challenge_id
        self.progress_value = progress_value
        self.target_value = target_value
        self.notes = notes

    def __repr__(self):
        return f"<ChallengeProgress {self.id}: User {self.user_id} - Challenge {self.challenge_id} - {self.progress_value}/{self.target_value}>"

    @property
    def completion_percentage(self):
        """Calculate completion percentage"""
        if self.target_value == 0:
            return 0
        return min(100, (self.progress_value / self.target_value) * 100)

    def to_dict(self):
        """Convert progress to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'challenge_id': self.challenge_id,
            'progress_value': self.progress_value,
            'target_value': self.target_value,
            'completion_percentage': self.completion_percentage,
            'last_updated': self.last_updated.isoformat(),
            'notes': self.notes
        }