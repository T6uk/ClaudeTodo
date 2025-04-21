"""
Todo forms for creating and editing tasks
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

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
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], validators=[DataRequired()])
    assignee = SelectField('Assign To', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Task')