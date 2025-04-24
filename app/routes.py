# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, jsonify
from app import db
from app.models import Todo, User, Event, Category, Tag
from datetime import datetime, timedelta, date
from functools import wraps
import calendar
from dateutil.relativedelta import relativedelta
from sqlalchemy import or_, and_, func
from flask import send_from_directory
import requests
from bs4 import BeautifulSoup
from flask import jsonify
from datetime import datetime
from flask import render_template
import os

bp = Blueprint('main', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/static/sw.js')
def service_worker():
    """Serve the service worker with the right content type"""
    response = send_from_directory('static', 'sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response


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

            return redirect(url_for('main.index'))
        else:
            flash('Vale parool', 'danger')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.login'))


@bp.route('/')
@login_required
def index():
    # Get the active tab from query parameters, default to 'active'
    active_tab = request.args.get('tab', 'active')

    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    category_filter = request.args.get('category', 'all')
    assigned_filter = request.args.get('assigned', 'all')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'due_date')

    # Base query
    query = Todo.query

    # Apply tab filter first
    if active_tab == 'active':
        query = query.filter(Todo.deleted == False, Todo.completed == False)
    elif active_tab == 'completed':
        query = query.filter(Todo.deleted == False, Todo.completed == True)
    elif active_tab == 'deleted':
        query = query.filter(Todo.deleted == True)

    # Apply other filters only if not in deleted tab
    if active_tab != 'deleted':
        if priority_filter != 'all':
            query = query.filter(Todo.priority == priority_filter)

        if category_filter != 'all' and category_filter.isdigit():
            query = query.filter(Todo.category_id == int(category_filter))

        if assigned_filter != 'all' and assigned_filter.isdigit():
            query = query.filter(Todo.user_id == int(assigned_filter))

    # Apply search to all tabs
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(or_(
            Todo.title.ilike(search),
            Todo.description.ilike(search)
        ))

    # Apply sorting
    if sort_by == 'priority':
        # Custom ordering for priority
        query = query.order_by(
            # High priority first, then medium, then low
            func.case(
                (Todo.priority == 'high', 1),
                (Todo.priority == 'medium', 2),
                (Todo.priority == 'low', 3)
            ),
            Todo.due_date
        )
    elif sort_by == 'title':
        query = query.order_by(Todo.title)
    elif sort_by == 'created_at':
        query = query.order_by(Todo.created_at.desc())
    elif sort_by == 'updated_at':
        query = query.order_by(Todo.updated_at.desc())
    else:  # Default: due_date
        query = query.order_by(Todo.due_date)

    # Execute query
    todos = query.all()

    # Get tab counts for badges
    active_count = Todo.query.filter(Todo.deleted == False, Todo.completed == False).count()
    completed_count = Todo.query.filter(Todo.deleted == False, Todo.completed == True).count()
    deleted_count = Todo.query.filter(Todo.deleted == True).count()

    # Get data for filters
    users = User.query.all()
    categories = Category.query.all()

    return render_template('index.html',
                           todos=todos,
                           users=users,
                           categories=categories,
                           status_filter=status_filter,
                           priority_filter=priority_filter,
                           category_filter=category_filter,
                           assigned_filter=assigned_filter,
                           search_query=search_query,
                           sort_by=sort_by,
                           active_tab=active_tab,
                           active_count=active_count,
                           completed_count=completed_count,
                           deleted_count=deleted_count)


@bp.route('/dashboard')
@login_required
def dashboard():
    # Get current date for calculations
    now = datetime.now()
    today = now.date()

    # Calculate upcoming tasks (next 7 days)
    upcoming_end = today + timedelta(days=7)

    # Upcoming todos - limited to 5, exclude deleted
    upcoming_todos = Todo.query.filter(
        Todo.deleted == False,
        Todo.due_date >= now,
        Todo.due_date <= datetime.combine(upcoming_end, datetime.max.time())
    ).order_by(Todo.due_date).limit(5).all()

    # Upcoming events - limited to 5
    upcoming_events = Event.query.filter(
        Event.start_datetime >= now
    ).order_by(Event.start_datetime).limit(5).all()

    # Statistics calculations - exclude deleted todos
    total_todos = Todo.query.filter(Todo.deleted == False).count()
    completed_todos = Todo.query.filter(Todo.deleted == False, Todo.completed == True).count()

    # Calculate due soon (next 48 hours) and overdue
    due_soon_cutoff = now + timedelta(hours=48)
    due_soon = Todo.query.filter(
        Todo.deleted == False,
        Todo.completed == False,
        Todo.due_date >= now,
        Todo.due_date <= due_soon_cutoff
    ).count()

    overdue = Todo.query.filter(
        Todo.deleted == False,
        Todo.completed == False,
        Todo.due_date < now
    ).count()

    # Calculate completion rate
    completion_rate = int((completed_todos / total_todos) * 100) if total_todos > 0 else 0

    # Calculate priority distribution - exclude deleted
    priority_counts = {
        'high': Todo.query.filter(Todo.deleted == False, Todo.priority == 'high').count(),
        'medium': Todo.query.filter(Todo.deleted == False, Todo.priority == 'medium').count(),
        'low': Todo.query.filter(Todo.deleted == False, Todo.priority == 'low').count()
    }

    # Calculate priority percentages
    priority_percentages = {
        'high': int((priority_counts['high'] / total_todos) * 100) if total_todos > 0 else 0,
        'medium': int((priority_counts['medium'] / total_todos) * 100) if total_todos > 0 else 0,
        'low': int((priority_counts['low'] / total_todos) * 100) if total_todos > 0 else 0
    }

    # Categories with task counts - exclude deleted todos
    categories = Category.query.all()
    categories_with_counts = []

    for category in categories:
        count = Todo.query.filter(Todo.deleted == False, Todo.category_id == category.id).count()
        if count > 0:
            categories_with_counts.append({
                'id': category.id,
                'name': category.name,
                'color': category.color,
                'count': count
            })

    # Sort categories by count (descending)
    categories_with_counts = sorted(categories_with_counts, key=lambda x: x['count'], reverse=True)

    # Combine stats into a single object
    stats = {
        'total_todos': total_todos,
        'completed_todos': completed_todos,
        'due_soon': due_soon,
        'overdue': overdue,
        'completion_rate': completion_rate,
        'priority_counts': priority_counts,
        'priority_percentages': priority_percentages
    }

    return render_template('dashboard.html',
                           stats=stats,
                           upcoming_todos=upcoming_todos,
                           upcoming_events=upcoming_events,
                           categories_with_counts=categories_with_counts)


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
        category_id = request.form.get('category_id')
        tags_input = request.form.get('tags', '')

        # Convert empty category_id to None
        if not category_id or category_id == '':
            category_id = None
        else:
            category_id = int(category_id)

        todo = Todo(
            title=title,
            description=description,
            due_date=due_date,
            user_id=user_id,
            created_by_id=created_by_id,
            priority=priority,
            category_id=category_id,
            deleted=False  # Explicitly set to False
        )

        # Process tags
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for tag_name in tag_names:
                # Check if tag exists, create if not
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                todo.tags.append(tag)

        db.session.add(todo)
        db.session.commit()
        flash('Ülesanne edukalt loodud!', 'success')
        return redirect(url_for('main.index'))

    users = User.query.all()
    categories = Category.query.all()
    return render_template('create_todo.html', users=users, categories=categories)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_todo(id):
    todo = Todo.query.get_or_404(id)

    # Don't allow editing deleted todos
    if todo.deleted:
        flash('Kustutatud ülesandeid ei saa muuta. Taastage ülesanne enne muutmist.', 'danger')
        return redirect(url_for('main.index', tab='deleted'))

    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.description = request.form.get('description')
        due_date_str = request.form.get('due_date')
        todo.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        todo.user_id = int(request.form.get('user_id'))
        todo.priority = request.form.get('priority')
        todo.completed = 'completed' in request.form

        # Update category
        category_id = request.form.get('category_id')
        if not category_id or category_id == '':
            todo.category_id = None
        else:
            todo.category_id = int(category_id)

        # Update tags
        tags_input = request.form.get('tags', '')

        # Remove all existing tags
        todo.tags = []

        # Add new tags
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                todo.tags.append(tag)

        db.session.commit()
        flash('Ülesanne edukalt uuendatud!', 'success')

        # Determine which tab to return to based on completion status
        if todo.completed:
            return redirect(url_for('main.index', tab='completed'))
        else:
            return redirect(url_for('main.index', tab='active'))

    users = User.query.all()
    categories = Category.query.all()
    # Format date for the datetime-local input
    formatted_date = todo.due_date.strftime('%Y-%m-%dT%H:%M')
    # Format tags as comma-separated string
    tags_string = ', '.join([tag.name for tag in todo.tags])

    return render_template('edit_todo.html',
                           todo=todo,
                           users=users,
                           categories=categories,
                           formatted_date=formatted_date,
                           tags_string=tags_string)


@bp.route('/delete/<int:id>')
@login_required
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.deleted = True  # Soft delete
    db.session.commit()
    flash('Ülesanne liigutatud prügikasti!', 'success')
    return redirect(url_for('main.index', tab=request.args.get('tab', 'active')))


@bp.route('/restore/<int:id>')
@login_required
def restore_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.deleted = False
    db.session.commit()
    flash('Ülesanne taastatud!', 'success')
    return redirect(url_for('main.index', tab='deleted'))


@bp.route('/permanent_delete/<int:id>')
@login_required
def permanent_delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('Ülesanne jäädavalt kustutatud!', 'success')
    return redirect(url_for('main.index', tab='deleted'))


@bp.route('/toggle_complete/<int:id>')
@login_required
def toggle_complete(id):
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    status = "lõpetatud" if todo.completed else "märgitud aktiivseks"
    flash(f'Ülesanne {status}!', 'success')

    # Determine which tab to return to
    tab = request.args.get('tab', 'active')
    return redirect(url_for('main.index', tab=tab))


# User management routes
@bp.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        avatar_color = request.form.get('avatar_color', 'blue')

        # Check if user with same name or email already exists
        existing_user = User.query.filter(
            or_(User.name == name, User.email == email)
        ).first()

        if existing_user:
            flash('Sellise nime või e-postiga kasutaja on juba olemas.', 'danger')
            return render_template('create_user.html')

        user = User(name=name, email=email, avatar_color=avatar_color)
        db.session.add(user)
        db.session.commit()
        flash('Kasutaja edukalt loodud!', 'success')
        return redirect(url_for('main.users'))

    return render_template('create_user.html')


@bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        avatar_color = request.form.get('avatar_color')

        # Check if another user has the same name or email
        existing_user = User.query.filter(
            User.id != id,
            or_(User.name == name, User.email == email)
        ).first()

        if existing_user:
            flash('Teine kasutaja sama nime või e-postiga on juba olemas.', 'danger')
            return render_template('edit_user.html', user=user)

        user.name = name
        user.email = email
        user.avatar_color = avatar_color

        db.session.commit()
        flash('Kasutaja edukalt uuendatud!', 'success')
        return redirect(url_for('main.users'))

    return render_template('edit_user.html', user=user)


@bp.route('/users/delete/<int:id>')
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)

    # Check if user has assigned tasks or created tasks/events
    has_todos = Todo.query.filter(
        or_(Todo.user_id == id, Todo.created_by_id == id)
    ).first() is not None

    has_events = Event.query.filter(Event.created_by_id == id).first() is not None

    if has_todos or has_events:
        flash('Ei saa kustutada kasutajat, kellel on ülesandeid või sündmusi.', 'danger')
        return redirect(url_for('main.users'))

    db.session.delete(user)
    db.session.commit()
    flash('Kasutaja edukalt kustutatud!', 'success')
    return redirect(url_for('main.users'))


# Category management routes
@bp.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)


@bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color', 'blue')

        # Check if category with same name already exists
        existing_category = Category.query.filter_by(name=name).first()

        if existing_category:
            flash('Sellise nimega kategooria on juba olemas.', 'danger')
            return render_template('create_category.html')

        category = Category(name=name, color=color)
        db.session.add(category)
        db.session.commit()
        flash('Kategooria edukalt loodud!', 'success')
        return redirect(url_for('main.categories'))

    return render_template('create_category.html')


@bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color')

        # Check if another category has the same name
        existing_category = Category.query.filter(
            Category.id != id,
            Category.name == name
        ).first()

        if existing_category:
            flash('Teine kategooria sama nimega on juba olemas.', 'danger')
            return render_template('edit_category.html', category=category)

        category.name = name
        category.color = color

        db.session.commit()
        flash('Kategooria edukalt uuendatud!', 'success')
        return redirect(url_for('main.categories'))

    return render_template('edit_category.html', category=category)


@bp.route('/categories/delete/<int:id>')
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)

    # Check if any tasks are assigned to this category
    has_todos = Todo.query.filter_by(category_id=id).first() is not None

    if has_todos:
        flash('Ei saa kustutada kategooriat, mis on seotud ülesannetega. Esmalt määra ülesannetele teine kategooria.',
              'danger')
        return redirect(url_for('main.categories'))

    db.session.delete(category)
    db.session.commit()
    flash('Kategooria edukalt kustutatud!', 'success')
    return redirect(url_for('main.categories'))


# Calendar/Events routes (remaining routes unchanged)
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
        flash('Sündmus edukalt loodud!', 'success')

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
        flash('Sündmus edukalt uuendatud!', 'success')

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
    flash('Sündmus edukalt kustutatud!', 'success')
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


@bp.route('/api/check-updates')
@login_required
def check_updates():
    """API endpoint to check if there are any updates"""
    last_update_time = request.args.get('last_update')
    if not last_update_time:
        return jsonify({"has_updates": True})

    try:
        last_update = datetime.fromisoformat(last_update_time.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({"has_updates": True})

    # Check if there are any todos or events updated after the last update time
    recent_todos = Todo.query.filter(Todo.updated_at > last_update).first()
    recent_events = Event.query.filter(Event.updated_at > last_update).first()

    has_updates = recent_todos is not None or recent_events is not None

    return jsonify({
        "has_updates": has_updates,
        "current_time": datetime.utcnow().isoformat() + 'Z'
    })


@bp.route('/tablet')
@login_required
def tablet_view():
    # Get current date and time
    now = datetime.now()
    today = now.date()

    # Get important todos (prioritized)
    # 1. First, get overdue tasks
    overdue_todos = Todo.query.filter(
        Todo.completed == False,
        Todo.due_date < now
    ).order_by(Todo.due_date).limit(5).all()

    # 2. Next, get tasks due today
    today_todos = Todo.query.filter(
        Todo.completed == False,
        Todo.due_date >= now,
        func.date(Todo.due_date) == today
    ).order_by(Todo.due_date).limit(5).all()

    # 3. Get high priority tasks
    high_priority_todos = Todo.query.filter(
        Todo.completed == False,
        Todo.priority == 'high',
        Todo.due_date >= now,
        func.date(Todo.due_date) > today
    ).order_by(Todo.due_date).limit(5).all()

    # 4. Medium priority tasks
    medium_priority_todos = Todo.query.filter(
        Todo.completed == False,
        Todo.priority == 'medium',
        Todo.due_date >= now,
        func.date(Todo.due_date) > today
    ).order_by(Todo.due_date).limit(3).all()

    # 5. Low priority tasks
    low_priority_todos = Todo.query.filter(
        Todo.completed == False,
        Todo.priority == 'low',
        Todo.due_date >= now,
        func.date(Todo.due_date) > today
    ).order_by(Todo.due_date).limit(3).all()

    # Combine and prioritize todos
    all_todos = []
    all_todos.extend(overdue_todos)
    all_todos.extend(today_todos)
    all_todos.extend(high_priority_todos)
    all_todos.extend(medium_priority_todos)
    all_todos.extend(low_priority_todos)

    # Limit to 3 tasks and mark their status
    todos = all_todos[:3]
    for todo in todos:
        if todo.due_date < now:
            todo.is_overdue = True
            todo.is_today = False
        elif todo.due_date.date() == today:
            todo.is_overdue = False
            todo.is_today = True
        else:
            todo.is_overdue = False
            todo.is_today = False

    # Get upcoming events (next 7 days)
    upcoming_end = today + timedelta(days=7)
    events = Event.query.filter(
        Event.start_datetime >= now,
        Event.start_datetime <= datetime.combine(upcoming_end, datetime.max.time())
    ).order_by(Event.start_datetime).limit(3).all()

    return render_template('tablet_view.html',
                           todos=todos,
                           events=events,
                           now=now,
                           today=today,
                           timedelta=timedelta)


@bp.route('/api/weather-tartu')
def weather_tartu():
    try:
        API_KEY = "8hfajKkGs4NE6PzR8RUQ7pDLuWnUNNs9"  # <- use your actual API key
        LOCATION_KEY = "131136"   # Tartu

        # AccuWeather API URL
        url = f"https://dataservice.accuweather.com/currentconditions/v1/{LOCATION_KEY}?apikey={API_KEY}"

        response = requests.get(url)
        data = response.json()

        weather = data[0]
        temperature = f"{weather['Temperature']['Metric']['Value']}°C"
        condition = weather['WeatherText']

        # Weather icon mapping (optional)
        icons = {
            'Sunny': '☀️',
            'Clear': '☀️',
            'Partly Sunny': '🌤️',
            'Partly Cloudy': '⛅',
            'Cloudy': '☁️',
            'Rain': '🌧️',
            'Showers': '🌦️',
            'Snow': '❄️',
            'Fog': '🌫️',
            'Windy': '💨',
        }

        icon = icons.get(condition, '🌡️')

        return jsonify({
            'temp': temperature,
            'condition': condition,
            'location': 'Tartu',
            'icon': icon,
            'success': True
        })

    except Exception as e:
        return jsonify({
            'temp': '---',
            'condition': '---',
            'location': 'Tartu',
            'icon': '💤',
            'success': False,
            'error': str(e)
        })


@bp.route('/morning-notification-status')
def morning_notification_status():
    """API endpoint to check if morning notification should be shown"""
    now = datetime.now()
    hour = now.hour

    # Return morning notification status
    return jsonify({
        'shouldShow': 7 <= hour < 9,
        'currentHour': hour,
        'message': "Tere hommikust Musi! Armastan Sind!",
        'currentTime': now.strftime('%Y-%m-%d %H:%M:%S')
    })