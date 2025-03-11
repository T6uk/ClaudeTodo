"""
Event model for calendar management
"""
from datetime import datetime
from app import db
from sqlalchemy.ext.associationproxy import association_proxy

# Association table for many-to-many relationship between events and users
event_attendees = db.Table('event_attendees',
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Event(db.Model):
    """
    Event model for calendar management

    Attributes:
        id (int): Primary key
        title (str): Event title
        description (str): Event description
        start_time (datetime): Event start time
        end_time (datetime): Event end time
        all_day (bool): Whether event lasts all day
        location (str): Event location
        color (str): Event display color
        created_at (datetime): Event creation timestamp
        updated_at (datetime): Event last update timestamp
        creator_id (int): User ID of event creator
        attendees (list): Users assigned to this event
    """
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    all_day = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(20), default="#A1B2D4")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id], backref=db.backref('created_events', lazy='dynamic'))
    attendees = db.relationship('User', secondary=event_attendees, backref=db.backref('events', lazy='dynamic'))

    def __init__(self, title, start_time, end_time, creator_id, description=None,
                 location=None, all_day=False, color="#A1B2D4"):
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.all_day = all_day
        self.location = location
        self.color = color
        self.creator_id = creator_id

    def __repr__(self):
        return f"<Event {self.id}: {self.title}>"

    def to_dict(self):
        """Convert event to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start': self.start_time.isoformat(),
            'end': self.end_time.isoformat(),
            'allDay': self.all_day,
            'location': self.location,
            'color': self.color,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'creator_id': self.creator_id,
            'creator_name': self.creator.username,
            'attendees': [{'id': user.id, 'username': user.username} for user in self.attendees]
        }