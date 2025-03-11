"""
Body metrics model for tracking physical measurements
"""
from datetime import datetime
from app import db


class BodyMetrics(db.Model):
    """
    Body metrics model for tracking physical measurements over time

    Attributes:
        id (int): Primary key
        weight (float): Weight in kg
        height (float): Height in cm
        body_fat (float): Body fat percentage
        bmi (float): Body Mass Index (calculated)
        waist (float): Waist measurement in cm
        chest (float): Chest measurement in cm
        arms (float): Arms measurement in cm
        thighs (float): Thighs measurement in cm
        date (datetime): Date of measurement
        notes (str): Additional notes
        user_id (int): User ID
    """
    __tablename__ = 'body_metrics'

    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    body_fat = db.Column(db.Float, nullable=True)
    bmi = db.Column(db.Float, nullable=True)
    waist = db.Column(db.Float, nullable=True)
    chest = db.Column(db.Float, nullable=True)
    arms = db.Column(db.Float, nullable=True)
    thighs = db.Column(db.Float, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('body_metrics', lazy='dynamic'))

    def __init__(self, user_id, date=None, weight=None, height=None, body_fat=None,
                 waist=None, chest=None, arms=None, thighs=None, notes=None):
        self.user_id = user_id
        self.date = date or datetime.utcnow()
        self.weight = weight
        self.height = height
        self.body_fat = body_fat
        self.waist = waist
        self.chest = chest
        self.arms = arms
        self.thighs = thighs
        self.notes = notes

        # Calculate BMI if weight and height are provided
        if weight and height and height > 0:
            self.bmi = weight / ((height / 100) ** 2)
        else:
            self.bmi = None

    def __repr__(self):
        return f"<BodyMetrics {self.id}: {self.date.strftime('%Y-%m-%d')}>"

    def to_dict(self):
        """Convert body metrics to dictionary"""
        return {
            'id': self.id,
            'weight': self.weight,
            'height': self.height,
            'body_fat': self.body_fat,
            'bmi': self.bmi,
            'waist': self.waist,
            'chest': self.chest,
            'arms': self.arms,
            'thighs': self.thighs,
            'date': self.date.isoformat() if self.date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        }