"""
Workout model for tracking exercise activities
"""
from datetime import datetime
from app import db


class Workout(db.Model):
    """
    Workout model for tracking exercise sessions

    Attributes:
        id (int): Primary key
        title (str): Workout title/name
        workout_type (str): Type of workout (cardio, strength, etc.)
        duration (int): Duration in minutes
        intensity (str): Workout intensity level
        calories_burned (int): Estimated calories burned
        notes (str): Additional notes about the workout
        date (datetime): Date and time of the workout
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
        user_id (int): User ID who recorded the workout
    """
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    workout_type = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    intensity = db.Column(db.String(20), nullable=True)
    calories_burned = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('workouts', lazy='dynamic'))

    def __init__(self, title, workout_type, duration, user_id, intensity=None,
                 calories_burned=None, notes=None, date=None):
        self.title = title
        self.workout_type = workout_type
        self.duration = duration
        self.intensity = intensity
        self.calories_burned = calories_burned
        self.notes = notes
        self.date = date or datetime.utcnow()
        self.user_id = user_id

    def __repr__(self):
        return f"<Workout {self.id}: {self.title}>"

    def to_dict(self):
        """Convert workout to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'workout_type': self.workout_type,
            'duration': self.duration,
            'intensity': self.intensity,
            'calories_burned': self.calories_burned,
            'notes': self.notes,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id,
            'username': self.user.username
        }