"""
Health forms for workout and meal tracking
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, DateTimeField, SubmitField, \
    FieldList, FormField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class ExerciseForm(FlaskForm):
    """Form for individual exercise entries"""
    name = StringField('Exercise Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    sets = IntegerField('Sets', validators=[
        Optional(),
        NumberRange(min=1, message='Number of sets must be positive')
    ])
    reps = IntegerField('Reps', validators=[
        Optional(),
        NumberRange(min=1, message='Number of reps must be positive')
    ])
    weight = FloatField('Weight (kg)', validators=[
        Optional(),
        NumberRange(min=0, message='Weight must be a positive number')
    ])
    duration = IntegerField('Duration (seconds)', validators=[
        Optional(),
        NumberRange(min=1, message='Duration must be positive')
    ])
    distance = FloatField('Distance (km)', validators=[
        Optional(),
        NumberRange(min=0, message='Distance must be a positive number')
    ])
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=200)
    ])


class WorkoutForm(FlaskForm):
    """Form for creating and editing workouts"""
    title = StringField('Workout Title', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    workout_type = SelectField('Workout Type', choices=[
        ('cardio', 'Cardio'),
        ('strength', 'Strength Training'),
        ('flexibility', 'Flexibility & Stretching'),
        ('sports', 'Sports & Recreation'),
        ('hiit', 'HIIT'),
        ('crossfit', 'CrossFit'),
        ('yoga', 'Yoga'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[
        DataRequired(),
        NumberRange(min=1, max=1440, message='Duration must be between 1 minute and 24 hours')
    ])
    intensity = SelectField('Intensity', choices=[
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('very_high', 'Very High')
    ], validators=[Optional()])
    calories_burned = IntegerField('Calories Burned', validators=[
        Optional(),
        NumberRange(min=0, message='Calories must be a positive number')
    ])
    date = DateTimeField('Workout Date & Time', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired()
    ])
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=500)
    ])
    completed = BooleanField('Mark as Completed', default=True)
    favorite = BooleanField('Add to Favorites', default=False)
    submit = SubmitField('Save Workout')


class MealForm(FlaskForm):
    """Form for creating and editing meals"""
    name = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    food_items = TextAreaField('Food Items', validators=[
        DataRequired(),
        Length(min=3, max=1000)
    ])
    calories = IntegerField('Calories', validators=[
        Optional(),
        NumberRange(min=0, message='Calories must be a positive number')
    ])
    protein = FloatField('Protein (g)', validators=[
        Optional(),
        NumberRange(min=0, message='Protein must be a positive number')
    ])
    carbs = FloatField('Carbohydrates (g)', validators=[
        Optional(),
        NumberRange(min=0, message='Carbohydrates must be a positive number')
    ])
    fat = FloatField('Fat (g)', validators=[
        Optional(),
        NumberRange(min=0, message='Fat must be a positive number')
    ])
    meal_time = DateTimeField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired()
    ])
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=500)
    ])
    submit = SubmitField('Save Meal')


class BodyMetricsForm(FlaskForm):
    """Form for tracking body metrics"""
    weight = FloatField('Weight (kg)', validators=[
        Optional(),
        NumberRange(min=0, message='Weight must be a positive number')
    ])
    height = FloatField('Height (cm)', validators=[
        Optional(),
        NumberRange(min=0, message='Height must be a positive number')
    ])
    body_fat = FloatField('Body Fat (%)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Body fat must be between 0 and 100')
    ])
    waist = FloatField('Waist (cm)', validators=[
        Optional(),
        NumberRange(min=0, message='Waist must be a positive number')
    ])
    chest = FloatField('Chest (cm)', validators=[
        Optional(),
        NumberRange(min=0, message='Chest must be a positive number')
    ])
    arms = FloatField('Arms (cm)', validators=[
        Optional(),
        NumberRange(min=0, message='Arms must be a positive number')
    ])
    thighs = FloatField('Thighs (cm)', validators=[
        Optional(),
        NumberRange(min=0, message='Thighs must be a positive number')
    ])
    date = DateTimeField('Date', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired()
    ])
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=500)
    ])
    submit = SubmitField('Save Measurements')


class WaterIntakeForm(FlaskForm):
    """Form for tracking water intake"""
    amount = FloatField('Amount (ml)', validators=[
        DataRequired(),
        NumberRange(min=0, message='Amount must be a positive number')
    ])
    date = DateTimeField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired()
    ])
    submit = SubmitField('Add Water Intake')
