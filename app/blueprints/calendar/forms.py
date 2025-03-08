from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    start_time = DateTimeField('Start Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_time = DateTimeField('End Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    all_day = BooleanField('All Day Event')
    color = SelectField('Color', choices=[
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('red', 'Red'),
        ('orange', 'Orange'),
        ('purple', 'Purple'),
        ('teal', 'Teal')
    ])
    submit = SubmitField('Save')