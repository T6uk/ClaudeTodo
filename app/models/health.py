from datetime import datetime
from app import db


class HealthRecord(db.Model):
    __tablename__ = 'health_records'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float, nullable=True)  # in kg
    height = db.Column(db.Float, nullable=True)  # in cm
    blood_pressure_systolic = db.Column(db.Integer, nullable=True)  # in mmHg
    blood_pressure_diastolic = db.Column(db.Integer, nullable=True)  # in mmHg
    heart_rate = db.Column(db.Integer, nullable=True)  # in bpm
    sleep_hours = db.Column(db.Float, nullable=True)
    water_intake = db.Column(db.Float, nullable=True)  # in liters
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<HealthRecord for {self.date}>'

    @property
    def bmi(self):
        """Calculate Body Mass Index if weight and height are available"""
        if self.weight and self.height:
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 2)
        return None