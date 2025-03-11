"""
Challenge model for user challenges
"""
from datetime import datetime
from app import db

# Association table for many-to-many relationship between challenges and participants
challenge_participants = db.Table('challenge_participants',
                                  db.Column('challenge_id', db.Integer, db.ForeignKey('challenges.id'),
                                            primary_key=True),
                                  db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
                                  )


class Challenge(db.Model):
    """
    Challenge model for activity challenges between users

    Attributes:
        id (int): Primary key
        title (str): Challenge title
        description (str): Challenge description
        start_date (datetime): Challenge start date
        end_date (datetime): Challenge end date
        created_at (datetime): Challenge creation timestamp
        updated_at (datetime): Challenge last update timestamp
        status (str): Challenge status (active, completed, deleted)
        creator_id (int): User ID of challenge creator
        participants (list): Users participating in this challenge
    """
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'deleted'

    # Foreign keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id],
                              backref=db.backref('created_challenges', lazy='dynamic'))
    participants = db.relationship('User', secondary=challenge_participants,
                                   backref=db.backref('challenges', lazy='dynamic'))

    def __init__(self, title, creator_id, description=None, start_date=None, end_date=None):
        self.title = title
        self.description = description
        self.start_date = start_date or datetime.utcnow()
        self.end_date = end_date
        self.creator_id = creator_id
        self.status = 'active'

    def __repr__(self):
        return f"<Challenge {self.id}: {self.title}>"

    def to_dict(self):
        """Convert challenge to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'creator_id': self.creator_id,
            'creator_name': self.creator.username,
            'participants': [{'id': user.id, 'username': user.username} for user in self.participants]
        }