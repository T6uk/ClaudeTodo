"""
Challenge forms for creating and editing challenges
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectMultipleField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional
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
    start_date = DateTimeField('Start Date', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired()
    ])
    end_date = DateTimeField('End Date', format='%Y-%m-%dT%H:%M', validators=[
        Optional()
    ])
    participants = MultiCheckboxField('Participants', coerce=int)
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('deleted', 'Deleted')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Challenge')