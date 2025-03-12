# app/models/dashboard_widget.py
from app import db
from datetime import datetime

class DashboardWidget(db.Model):
    """
    Dashboard widget model for storing user dashboard customization

    Attributes:
        id (int): Primary key
        user_id (int): User ID
        widget_type (str): Type of widget (workout, nutrition, water, etc.)
        position (int): Position/order of widget on dashboard
        enabled (bool): Whether widget is enabled/visible
        size (str): Size of widget (small, medium, large)
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
    """
    __tablename__ = 'dashboard_widgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    widget_type = db.Column(db.String(50), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    size = db.Column(db.String(20), default='medium')  # small, medium, large
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dashboard_widgets', lazy='dynamic', cascade='all, delete-orphan'))

    def __init__(self, user_id, widget_type, position, enabled=True, size='medium'):
        self.user_id = user_id
        self.widget_type = widget_type
        self.position = position
        self.enabled = enabled
        self.size = size

    def __repr__(self):
        return f"<DashboardWidget {self.id}: {self.widget_type} - Pos {self.position}>"

    def to_dict(self):
        """Convert dashboard widget to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'widget_type': self.widget_type,
            'position': self.position,
            'enabled': self.enabled,
            'size': self.size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }