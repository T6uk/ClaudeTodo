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
        Optional(),
        NumberRange(min=0, message="Calories burned must be a positive number")
    ])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Save')


class ExerciseForm(FlaskForm):
    name = StringField('Exercise Name', validators=[DataRequired(), Length(min=1, max=100)])
    sets = IntegerField('Sets', validators=[Optional(), NumberRange(min=1)])
    reps = IntegerField('Reps', validators=[Optional(), NumberRange(min=1)])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Add Exercise')
