"""
Meal model for tracking food intake and nutrition
"""
from datetime import datetime
from app import db


class Meal(db.Model):
    """
    Meal model for tracking food and nutrition

    Attributes:
        id (int): Primary key
        name (str): Meal name (e.g., Breakfast, Lunch)
        food_items (str): Description of food items in the meal
        calories (int): Total calories in the meal
        protein (float): Protein content in grams
        carbs (float): Carbohydrate content in grams
        fat (float): Fat content in grams
        meal_time (datetime): When the meal was consumed
        notes (str): Additional notes about the meal
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
        user_id (int): User ID who recorded the meal
    """
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    food_items = db.Column(db.Text, nullable=False)
    calories = db.Column(db.Integer, nullable=True)
    protein = db.Column(db.Float, nullable=True)  # in grams
    carbs = db.Column(db.Float, nullable=True)  # in grams
    fat = db.Column(db.Float, nullable=True)  # in grams
    meal_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('meals', lazy='dynamic'))

    def __init__(self, name, food_items, user_id, calories=None, protein=None,
                 carbs=None, fat=None, meal_time=None, notes=None):
        self.name = name
        self.food_items = food_items
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fat = fat
        self.meal_time = meal_time or datetime.utcnow()
        self.notes = notes
        self.user_id = user_id

    def __repr__(self):
        return f"<Meal {self.id}: {self.name}>"

    def to_dict(self):
        """Convert meal to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'food_items': self.food_items,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'meal_time': self.meal_time.isoformat() if self.meal_time else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'username': self.user.username
        }
