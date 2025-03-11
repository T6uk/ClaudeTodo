"""
Event forms for creating and editing calendar events
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, SelectMultipleField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class EventForm(FlaskForm):
    """Form for creating and editing calendar events"""
    title = StringField('Event Title', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500)
    ])
    start_time = DateTimeField('Start Time', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired()
    ])
    end_time = DateTimeField('End Time', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired()
    ])
    all_day = BooleanField('All Day Event')
    location = StringField('Location', validators=[
        Optional(),
        Length(max=200)
    ])
    color = SelectField('Color', choices=[
        ('#A1B2D4', 'Blue'),
        ('#8090B2', 'Dark Blue'),
        ('#57A773', 'Green'),
        ('#F3C969', 'Yellow'),
        ('#D76464', 'Red'),
        ('#B7C9E8', 'Light Blue'),
        ('#E0E4F2', 'Lavender')
    ], validators=[Optional()])
    attendees = MultiCheckboxField('Attendees', coerce=int)
    submit = SubmitField('Save Event')