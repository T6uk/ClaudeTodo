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
        category (str): Challenge category
        start_date (datetime): Challenge start date
        end_date (datetime): Challenge end date
        created_at (datetime): Challenge creation timestamp
        updated_at (datetime): Challenge last update timestamp
        status (str): Challenge status (active, completed, deleted)
        creator_id (int): User ID of challenge creator
        target_value (float): Target goal for the challenge (optional)
        current_value (float): Current progress value (optional)
        measurement_unit (str): Unit of measurement (optional)
        participants (list): Users participating in this challenge
    """
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), default='General')
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'deleted'
    target_value = db.Column(db.Float, nullable=True)
    current_value = db.Column(db.Float, default=0.0)
    measurement_unit = db.Column(db.String(20), nullable=True)

    # Foreign keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id],
                              backref=db.backref('created_challenges', lazy='dynamic'))
    participants = db.relationship('User', secondary=challenge_participants,
                                   backref=db.backref('challenges', lazy='dynamic'))

    def __init__(self, title, creator_id, description=None, category='General',
                 start_date=None, end_date=None, target_value=None, measurement_unit=None):
        self.title = title
        self.description = description
        self.category = category
        self.start_date = start_date or datetime.utcnow()
        self.end_date = end_date
        self.creator_id = creator_id
        self.status = 'active'
        self.target_value = target_value
        self.current_value = 0.0
        self.measurement_unit = measurement_unit

    def __repr__(self):
        return f"<Challenge {self.id}: {self.title}>"

    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.target_value and self.target_value > 0:
            return min(100, (self.current_value / self.target_value) * 100)
        return 0

    @property
    def days_remaining(self):
        """Calculate days remaining until end date"""
        if self.end_date:
            remaining = (self.end_date - datetime.utcnow()).days
            return max(0, remaining)
        return None

    def to_dict(self):
        """Convert challenge to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'creator_id': self.creator_id,
            'creator_name': self.creator.username,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'measurement_unit': self.measurement_unit,
            'progress_percentage': self.progress_percentage,
            'days_remaining': self.days_remaining,
            'participants': [{'id': user.id, 'username': user.username} for user in self.participants]
        }