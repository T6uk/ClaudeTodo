"""
Calendar routes for managing events
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from datetime import datetime, timedelta
import json

from app import db
from app.models.user import User
from app.models.event import Event
from app.forms.event_forms import EventForm

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/calendar")
@login_required
def calendar():
    """Calendar view page"""
    form = EventForm()

    # Set up user choices for attendee field
    users = User.query.all()
    form.attendees.choices = [(u.id, u.username) for u in users]

    return render_template("calendar/calendar.html",
                           title="Calendar",
                           form=form)


@calendar_bp.route("/events", methods=["GET"])
@login_required
def get_events():
    """Get events for specified date range (for AJAX requests)"""
    # Get start and end parameters from request
    start = request.args.get('start', None)
    end = request.args.get('end', None)

    # Query events
    query = Event.query

    # Filter by date range if provided
    if start and end:
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        query = query.filter(Event.end_time >= start_date, Event.start_time <= end_date)

    events = query.all()
    event_list = [event.to_dict() for event in events]

    return jsonify(event_list)


@calendar_bp.route("/events/create", methods=["POST"])
@login_required
def create_event():
    """Create a new event"""
    form = EventForm()

    # Set up user choices for attendee field
    users = User.query.all()
    form.attendees.choices = [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        # Create new event
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            all_day=form.all_day.data,
            location=form.location.data,
            color=form.color.data,
            creator_id=current_user.id
        )

        # Add attendees
        if form.attendees.data:
            attendee_users = User.query.filter(User.id.in_(form.attendees.data)).all()
            event.attendees = attendee_users

        # Add to database
        db.session.add(event)
        db.session.commit()

        flash("Event created successfully!", "success")
        return redirect(url_for("calendar.calendar"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("calendar.calendar"))


@calendar_bp.route("/events/<int:event_id>", methods=["GET"])
@login_required
def get_event(event_id):
    """Get event details"""
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict())


@calendar_bp.route("/events/<int:event_id>/update", methods=["POST"])
@login_required
def update_event(event_id):
    """Update an existing event"""
    event = Event.query.get_or_404(event_id)
    form = EventForm()

    # Set up user choices for attendee field
    users = User.query.all()
    form.attendees.choices = [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        # Update event fields
        event.title = form.title.data
        event.description = form.description.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.all_day = form.all_day.data
        event.location = form.location.data
        event.color = form.color.data

        # Update attendees
        if form.attendees.data:
            attendee_users = User.query.filter(User.id.in_(form.attendees.data)).all()
            event.attendees = attendee_users
        else:
            event.attendees = []

        db.session.commit()
        flash("Event updated successfully!", "success")
        return redirect(url_for("calendar.calendar"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("calendar.calendar"))


@calendar_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    """Delete an event"""
    event = Event.query.get_or_404(event_id)

    db.session.delete(event)
    db.session.commit()

    flash("Event deleted successfully!", "success")
    return redirect(url_for("calendar.calendar"))