from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, jsonify
from app import db
from app.models import Todo, User, Event
from datetime import datetime, timedelta, date
from functools import wraps
import calendar
from dateutil.relativedelta import relativedelta

bp = Blueprint('main', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        password = request.form.get('password')
        if password == current_app.config['APP_PASSWORD']:
            session['logged_in'] = True

            # Make the session permanent
            session.permanent = True
            # Session will expire after 30 days
            current_app.permanent_session_lifetime = timedelta(days=30)

            return redirect(url_for('main.index'))
        else:
            flash('Invalid password', 'danger')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.login'))


@bp.route('/')
@login_required
def index():
    todos = Todo.query.order_by(Todo.due_date).all()
    users = User.query.all()
    return render_template('index.html', todos=todos, users=users)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_todo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        user_id = int(request.form.get('user_id'))
        created_by_id = int(request.form.get('created_by_id'))
        priority = request.form.get('priority')

        todo = Todo(
            title=title,
            description=description,
            due_date=due_date,
            user_id=user_id,
            created_by_id=created_by_id,
            priority=priority
        )

        db.session.add(todo)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('create_todo.html', users=users)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_todo(id):
    todo = Todo.query.get_or_404(id)

    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        todo.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        todo.user_id = int(request.form.get('user_id'))
        todo.priority = request.form.get('priority')
        todo.completed = 'completed' in request.form

        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.index'))

    users = User.query.all()
    # Format date for the datetime-local input
    formatted_date = todo.due_date.strftime('%Y-%m-%dT%H:%M')
    return render_template('edit_todo.html', todo=todo, users=users, formatted_date=formatted_date)


@bp.route('/delete/<int:id>')
@login_required
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.index'))


@bp.route('/toggle_complete/<int:id>')
@login_required
def toggle_complete(id):
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    status = "completed" if todo.completed else "marked as active"
    flash(f'Task {status}!', 'success')
    return redirect(url_for('main.index'))


# Calendar/Events routes
@bp.route('/events')
@login_required
def events():
    view_type = request.args.get('view', 'month')
    date_str = request.args.get('date')

    if date_str:
        try:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = date.today()
    else:
        current_date = date.today()

    today = date.today()
    users = User.query.all()

    if view_type == 'day':
        # Day view
        start_date = current_date
        end_date = current_date
        day_start = datetime.combine(start_date, datetime.min.time())
        day_end = datetime.combine(end_date, datetime.max.time())

        # Improved query: get events that either:
        # 1. Start during this day
        # 2. End during this day
        # 3. Span across this day (start before, end after)
        events = Event.query.filter(
            ((Event.start_datetime >= day_start) & (Event.start_datetime <= day_end)) |  # Starts today
            ((Event.end_datetime >= day_start) & (Event.end_datetime <= day_end)) |  # Ends today
            ((Event.start_datetime <= day_start) & (Event.end_datetime >= day_end))  # Spans today
        ).order_by(Event.start_datetime).all()

        return render_template('events_day.html',
                               events=events,
                               current_date=current_date,
                               users=users,
                               today=today,
                               timedelta=timedelta,
                               now=datetime.now)

    elif view_type == 'week':
        # Week view - starting from Monday
        weekday = current_date.weekday()
        start_date = current_date - timedelta(days=weekday)
        end_date = start_date + timedelta(days=6)

        events = Event.query.filter(
            Event.start_datetime >= datetime.combine(start_date, datetime.min.time()),
            Event.start_datetime <= datetime.combine(end_date, datetime.max.time())
        ).order_by(Event.start_datetime).all()

        week_dates = [start_date + timedelta(days=i) for i in range(7)]

        return render_template('events_week.html',
                               events=events,
                               week_dates=week_dates,
                               current_date=current_date,
                               users=users,
                               today=today,
                               timedelta=timedelta)

    else:  # Default month view
        # Get first day of month and number of days
        first_day = current_date.replace(day=1)
        last_day = (first_day + relativedelta(months=1, days=-1))

        # Get events for this month
        events = Event.query.filter(
            Event.start_datetime >= datetime.combine(first_day, datetime.min.time()),
            Event.start_datetime <= datetime.combine(last_day, datetime.max.time())
        ).order_by(Event.start_datetime).all()

        # Prepare calendar data
        cal = calendar.monthcalendar(current_date.year, current_date.month)
        month_name = calendar.month_name[current_date.month]

        # Get previous and next month dates for navigation
        prev_month = first_day - timedelta(days=1)
        next_month = last_day + timedelta(days=1)

        return render_template('events.html',
                               calendar=cal,
                               month_name=month_name,
                               current_date=current_date,
                               events=events,
                               prev_month=prev_month,
                               next_month=next_month,
                               users=users,
                               today=today)


@bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_datetime_str = request.form.get('start_datetime')
        end_datetime_str = request.form.get('end_datetime')
        all_day = 'all_day' in request.form
        color = request.form.get('color')
        created_by_id = int(request.form.get('created_by_id'))

        # Parse datetime strings
        start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')

        # If all-day event, set end time to end of day
        if all_day:
            # If end_datetime is not provided or same as start, set it to end of day
            if not end_datetime_str or end_datetime_str == start_datetime_str:
                end_datetime = datetime.combine(start_datetime.date(), datetime.max.time())
            else:
                end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
                # Ensure end of day
                end_datetime = datetime.combine(end_datetime.date(), datetime.max.time())
        else:
            # Regular event with specific end time
            if not end_datetime_str:
                # Default to 1 hour after start
                end_datetime = start_datetime + timedelta(hours=1)
            else:
                end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')

        event = Event(
            title=title,
            description=description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            all_day=all_day,
            color=color,
            created_by_id=created_by_id
        )

        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')

        # Determine where to redirect based on the date of the event
        target_date = start_datetime.date().strftime('%Y-%m-%d')
        return redirect(url_for('main.events', date=target_date))

    # Get date from query string if provided
    date_str = request.args.get('date')
    if date_str:
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            # Set default time to current hour, next round hour
            now = datetime.now()
            start_hour = now.hour
            if now.minute > 30:
                start_hour += 1
            start_hour = min(start_hour, 23)  # Ensure within 24hr

            event_datetime = datetime.combine(event_date, datetime.min.time().replace(hour=start_hour))
            default_start = event_datetime.strftime('%Y-%m-%dT%H:%M')
            default_end = (event_datetime + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
        except ValueError:
            default_start = ''
            default_end = ''
    else:
        default_start = ''
        default_end = ''

    users = User.query.all()
    return render_template('create_event.html', users=users, default_start=default_start, default_end=default_end)


@bp.route('/events/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        start_datetime_str = request.form.get('start_datetime')
        end_datetime_str = request.form.get('end_datetime')
        event.all_day = 'all_day' in request.form
        event.color = request.form.get('color')

        # Parse datetime strings
        event.start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')

        # If all-day event, set end time to end of day
        if event.all_day:
            # If end_datetime is not provided or same as start, set it to end of day
            if not end_datetime_str or end_datetime_str == start_datetime_str:
                event.end_datetime = datetime.combine(event.start_datetime.date(), datetime.max.time())
            else:
                event.end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
                # Ensure end of day for all-day events
                event.end_datetime = datetime.combine(event.end_datetime.date(), datetime.max.time())
        else:
            # Regular event with specific end time
            if not end_datetime_str:
                # Default to 1 hour after start
                event.end_datetime = event.start_datetime + timedelta(hours=1)
            else:
                event.end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')

        db.session.commit()
        flash('Event updated successfully!', 'success')

        # Redirect to the event's date view
        target_date = event.start_datetime.date().strftime('%Y-%m-%d')
        return redirect(url_for('main.events', date=target_date))

    # Format dates for the datetime-local inputs
    formatted_start = event.start_datetime.strftime('%Y-%m-%dT%H:%M')
    formatted_end = event.end_datetime.strftime('%Y-%m-%dT%H:%M')

    users = User.query.all()
    return render_template('edit_event.html',
                           event=event,
                           users=users,
                           formatted_start=formatted_start,
                           formatted_end=formatted_end)


@bp.route('/events/delete/<int:id>')
@login_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    # Save the date before deleting for redirect
    target_date = event.start_datetime.date().strftime('%Y-%m-%d')

    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('main.events', date=target_date))


@bp.route('/events/detail/<int:id>')
@login_required
def event_detail(id):
    event = Event.query.get_or_404(id)
    return render_template('event_detail.html', event=event)


@bp.route('/events/api/get_events')
@login_required
def get_events_api():
    """API endpoint to get events in a date range for AJAX requests"""
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    if not start_date or not end_date:
        return jsonify([])

    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        end_dt = datetime.combine(end_dt, datetime.max.time())  # Include full end day
    except ValueError:
        return jsonify([])

    events = Event.query.filter(
        Event.start_datetime >= start_dt,
        Event.start_datetime <= end_dt
    ).all()

    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': event.end_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
            'allDay': event.all_day,
            'color': event.color,
            'url': url_for('main.event_detail', id=event.id)
        })

    return jsonify(events_data)
