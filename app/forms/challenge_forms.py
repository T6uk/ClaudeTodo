"""
Challenge forms for creating and editing challenges
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectMultipleField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class ChallengeForm(FlaskForm):
    """Form for creating and editing challenges"""
    title = StringField('Challenge Title', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000)
    ])
    category = SelectField('Category', choices=[
        ('General', 'General'),
        ('Fitness', 'Fitness'),
        ('Learning', 'Learning'),
        ('Productivity', 'Productivity'),
        ('Finance', 'Finance'),
        ('Health', 'Health'),
        ('Social', 'Social'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    start_date = DateTimeField('Start Date', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired()
    ])
    end_date = DateTimeField('End Date', format='%Y-%m-%dT%H:%M', validators=[
        Optional()
    ])
    target_value = FloatField('Target Goal', validators=[
        Optional(),
        NumberRange(min=0, message="Target goal must be positive")
    ])
    measurement_unit = StringField('Measurement Unit', validators=[
        Optional(),
        Length(max=20)
    ])
    participants = MultiCheckboxField('Participants', coerce=int)
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('deleted', 'Deleted')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Challenge')