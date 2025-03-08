from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Todo, CalendarEvent, Challenge, Workout, HealthRecord
from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import RegistrationForm, LoginForm, ChangePasswordForm


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')

    return render_template('auth/login.html', title='Login', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@auth_bp.route('/profile')
@login_required
def profile():
    # Count user's activities for the profile page
    todos_count = Todo.query.filter_by(user_id=current_user.id).count()
    events_count = CalendarEvent.query.filter_by(user_id=current_user.id).count()
    challenges_count = Challenge.query.filter_by(user_id=current_user.id).count()
    workouts_count = Workout.query.filter_by(user_id=current_user.id).count()
    health_records_count = HealthRecord.query.filter_by(user_id=current_user.id).count()

    # Create a placeholder for recent activities
    # In a real app, you might have a dedicated Activity model
    recent_activities = []

    # Get recent todos
    recent_todos = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.created_at.desc()).limit(2).all()
    for todo in recent_todos:
        recent_activities.append({
            'type': 'Todo',
            'color': 'primary',
            'description': f"{'Completed' if todo.completed else 'Created'} task: {todo.title}",
            'timestamp': todo.created_at
        })

    # Get recent events
    recent_events = CalendarEvent.query.filter_by(user_id=current_user.id).order_by(
        CalendarEvent.created_at.desc()).limit(2).all()
    for event in recent_events:
        recent_activities.append({
            'type': 'Event',
            'color': 'success',
            'description': f"Added event: {event.title}",
            'timestamp': event.created_at
        })

    # Get recent challenges
    recent_challenges = Challenge.query.filter_by(user_id=current_user.id).order_by(Challenge.created_at.desc()).limit(
        2).all()
    for challenge in recent_challenges:
        recent_activities.append({
            'type': 'Challenge',
            'color': 'info',
            'description': f"Created challenge: {challenge.title}",
            'timestamp': challenge.created_at
        })

    # Get recent workouts
    recent_workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.created_at.desc()).limit(
        2).all()
    for workout in recent_workouts:
        recent_activities.append({
            'type': 'Workout',
            'color': 'warning',
            'description': f"Logged {workout.workout_type} workout ({workout.duration} mins)",
            'timestamp': workout.created_at
        })

    # Sort all activities by timestamp, newest first
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    # Limit to the 5 most recent activities
    recent_activities = recent_activities[:5]

    return render_template('auth/profile.html',
                           title='Profile',
                           todos_count=todos_count,
                           events_count=events_count,
                           challenges_count=challenges_count,
                           workouts_count=workouts_count,
                           health_records_count=health_records_count,
                           recent_activities=recent_activities)


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.profile'))

        # Verify that the new passwords match
        if form.new_password.data != form.confirm_password.data:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('auth.profile'))

        # Update the password
        current_user.set_password(form.new_password.data)
        db.session.commit()

        flash('Your password has been updated!', 'success')
        return redirect(url_for('auth.profile'))

    # If there are form validation errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field}: {error}", 'danger')

    return redirect(url_for('auth.profile'))