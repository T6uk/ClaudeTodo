from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class WorkoutForm(FlaskForm):
    workout_type = SelectField('Workout Type', choices=[
        ('Cardio', 'Cardio'),
        ('Strength', 'Strength Training'),
        ('Flexibility', 'Flexibility'),
        ('HIIT', 'High-Intensity Interval Training'),
        ('Yoga', 'Yoga'),
        ('Pilates', 'Pilates'),
        ('CrossFit', 'CrossFit'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[
        DataRequired(),
        NumberRange(min=1, message="Duration must be at least 1 minute")
    ])
    calories_burned = IntegerField('Calories Burned', validators=[