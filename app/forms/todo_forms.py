"""
Todo forms for creating and editing tasks
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, SelectMultipleField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class TodoForm(FlaskForm):
    """Form for creating and editing todo tasks"""
    title = StringField('Task Title', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500)
    ])
    due_date = DateTimeField('Due Date', format='%Y-%m-%dT%H:%M', validators=[
        Optional()
    ])
    priority = SelectField('Priority', choices=[
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Medium'),
        ('4', 'High'),
        ('5', 'Very High')
    ], validators=[DataRequired()])
    assignees = MultiCheckboxField('Assignees', coerce=int)
    completed = BooleanField('Completed')
    submit = SubmitField('Save Task')