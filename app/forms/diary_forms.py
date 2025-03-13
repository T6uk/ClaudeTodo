"""
Diary forms for creating and editing journal entries
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class DiaryEntryForm(FlaskForm):
    """Form for creating and editing diary entries"""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=150)
    ])
    content = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=1)
    ])
    mood = SelectField('Mood', choices=[
        ('', 'Select Mood'),
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('anxious', 'Anxious'),
        ('calm', 'Calm'),
        ('excited', 'Excited'),
        ('tired', 'Tired'),
        ('neutral', 'Neutral'),
        ('other', 'Other')
    ], validators=[Optional()])
    category = SelectField('Category', choices=[
        ('', 'Select Category'),
        ('personal', 'Personal'),
        ('work', 'Work'),
        ('health', 'Health'),
        ('travel', 'Travel'),
        ('family', 'Family'),
        ('goals', 'Goals'),
        ('ideas', 'Ideas'),
        ('dreams', 'Dreams'),
        ('other', 'Other')
    ], validators=[Optional()])
    is_favorite = BooleanField('Favorite')
    is_private = BooleanField('Private')
    weather = StringField('Weather', validators=[
        Optional(),
        Length(max=50)
    ])
    location = StringField('Location', validators=[
        Optional(),
        Length(max=100)
    ])
    submit = SubmitField('Save Entry')

class DiarySearchForm(FlaskForm):
    """Form for searching diary entries"""
    query = StringField('Search', validators=[Optional()])
    mood = SelectField('Mood', choices=[
        ('', 'All Moods'),
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('anxious', 'Anxious'),
        ('calm', 'Calm'),
        ('excited', 'Excited'),
        ('tired', 'Tired'),
        ('neutral', 'Neutral'),
        ('other', 'Other')
    ], validators=[Optional()])
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('personal', 'Personal'),
        ('work', 'Work'),
        ('health', 'Health'),
        ('travel', 'Travel'),
        ('family', 'Family'),
        ('goals', 'Goals'),
        ('ideas', 'Ideas'),
        ('dreams', 'Dreams'),
        ('other', 'Other')
    ], validators=[Optional()])
    favorites_only = BooleanField('Favorites Only')
    date_from = StringField('From Date', validators=[Optional()])
    date_to = StringField('To Date', validators=[Optional()])
    submit = SubmitField('Search')