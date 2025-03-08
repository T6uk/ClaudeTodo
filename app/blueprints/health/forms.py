from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class HealthRecordForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=0)])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=0)])
    blood_pressure_systolic = IntegerField('Blood Pressure (Systolic)', validators=[Optional(), NumberRange(min=0)])
    blood_pressure_diastolic = IntegerField('Blood Pressure (Diastolic)', validators=[Optional(), NumberRange(min=0)])
    heart_rate = IntegerField('Heart Rate (bpm)', validators=[Optional(), NumberRange(min=0)])
    sleep_hours = FloatField('Sleep (hours)', validators=[Optional(), NumberRange(min=0, max=24)])
    water_intake = FloatField('Water Intake (liters)', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save')