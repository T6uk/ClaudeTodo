from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import CalendarEvent
from app.blueprints.calendar import calendar_bp
from app.blueprints.calendar.forms import EventForm
from datetime import datetime


@calendar_bp.route('/')
@login_required
def view_calendar():
    return render_template('calendar/calendar.html', title='Calendar')


@calendar_bp.route('/events')
@login_required
def get_events():
    start = request.args.get('start', type=str)
    end = request.args.get('end', type=str)

    # Convert to datetime objects if provided
    start_date = datetime.fromisoformat(start.replace('Z', '+00:00')) if start else None
    end_date = datetime.fromisoformat(end.replace('Z', '+00:00')) if end else None

    # Query events
    query = CalendarEvent.query.filter_by(user_id=current_user.id)
    if start_date:
        query = query.filter(CalendarEvent.end_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.start_time <= end_date)

    events = query.all()

    # Format for FullCalendar
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'allDay': event.all_day,
            'backgroundColor': event.color,
            'borderColor': event.color,
            'description': event.description
        })

    return jsonify(event_list)


@calendar_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_event():
    form = EventForm()
    if form.validate_on_submit():
        event = CalendarEvent(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            all_day=form.all_day.data,
            color=form.color.data,
            user_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('calendar.view_calendar'))

    # Pre-populate with date if provided in query string
    start_date = request.args.get('date')
    if start_date:
        try:
            form.start_time.data = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            form.end_time.data = form.start_time.data
        except ValueError:
            pass

    return render_template('calendar/event.html', title='New Event', form=form, is_update=False)


@calendar_bp.route('/<int:event_id>', methods=['GET', 'POST'])
@login_required
def view_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)

    # Ensure the current user owns this event
    if event.user_id != current_user.id:
        abort(403)

    return render_template('calendar/view.html', title=event.title, event=event)


@calendar_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)

    # Ensure the current user owns this event
    if event.user_id != current_user.id:
        abort(403)

    form = EventForm()

    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.all_day = form.all_day.data
        event.color = form.color.data
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('calendar.view_event', event_id=event.id))

    # Pre-fill the form with current data
    if request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.start_time.data = event.start_time
        form.end_time.data = event.end_time
        form.all_day.data = event.all_day
        form.color.data = event.color

    return render_template('calendar/event.html', title='Edit Event', form=form, is_update=True)


@calendar_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)

    # Ensure the current user owns this event
    if event.user_id != current_user.id:
        abort(403)

    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('calendar.view_calendar'))