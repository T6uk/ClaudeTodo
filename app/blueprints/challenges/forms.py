from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class ChallengeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    goal = StringField('Goal', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Save')

class ProgressForm(FlaskForm):
    progress = FloatField('Progress (%)', validators=[
        DataRequired(),
        NumberRange(min=0, max=100, message="Progress must be between 0 and 100")
    ])
    submit = SubmitField('Update Progress')