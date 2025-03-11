"""
Water intake model for tracking hydration
"""
from datetime import datetime
from app import db


class WaterIntake(db.Model):
    """
    Water intake model for tracking hydration

    Attributes:
        id (int): Primary key
        amount (float): Amount of water in ml
        date (datetime): Date and time of intake
        created_at (datetime): Record creation timestamp
        user_id (int): User ID
    """
    __tablename__ = 'water_intake'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)  # in ml
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('water_intake', lazy='dynamic'))

    def __init__(self, user_id, amount, date=None):
        self.user_id = user_id
        self.amount = amount
        self.date = date or datetime.utcnow()

    def __repr__(self):
        return f"<WaterIntake {self.id}: {self.amount}ml>"

    def to_dict(self):
        """Convert water intake to dictionary"""
        return {
            'id': self.id,
            'amount': self.amount,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id
        }