from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Optional

class TodoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    priority = SelectField('Priority', choices=[
        (0, 'Low'),
        (1, 'Medium'),
        (2, 'High')
    ], coerce=int)
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M', validators=[Optional()])
    submit = SubmitField('Save')

class TodoStatusForm(FlaskForm):
    completed = BooleanField('Completed')
    submit = SubmitField('Update Status')