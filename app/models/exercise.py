# app/models/exercise.py

"""
Exercise model for tracking individual exercises within workouts
"""
from datetime import datetime
from app import db


class Exercise(db.Model):
    """
    Exercise model for individual exercises within workouts

    Attributes:
        id (int): Primary key
        name (str): Exercise name
        sets (int): Number of sets performed
        reps (int): Number of repetitions per set
        weight (float): Weight used (if applicable)
        duration (int): Duration in seconds (if applicable)
        distance (float): Distance covered (if applicable)
        notes (str): Additional notes
        workout_id (int): Foreign key to parent workout
    """
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)  # in kg
    duration = db.Column(db.Integer, nullable=True)  # in seconds
    distance = db.Column(db.Float, nullable=True)  # in km
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)

    def __init__(self, name, workout_id, sets=None, reps=None, weight=None,
                 duration=None, distance=None, notes=None):
        self.name = name
        self.workout_id = workout_id
        self.sets = sets
        self.reps = reps
        self.weight = weight
        self.duration = duration
        self.distance = distance
        self.notes = notes

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name}>"

    def to_dict(self):
        """Convert exercise to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight,
            'duration': self.duration,
            'distance': self.distance,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'workout_id': self.workout_id
        }