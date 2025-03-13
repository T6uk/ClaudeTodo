# app/routes/diary.py (updated)
"""
Enhanced Diary routes for personal journal entries
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import desc, or_, func, extract
import csv
import io
from collections import defaultdict

from app import db
from app.models.diary import DiaryEntry
from app.forms.diary_forms import DiaryEntryForm, DiarySearchForm

diary_bp = Blueprint("diary", __name__)


@diary_bp.route("/diary")
@login_required
def diary():
    """Diary main page with list of entries"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Get filter parameters
    search_form = DiarySearchForm(request.args, meta={'csrf': False})
    query = request.args.get('query', '')
    mood = request.args.get('mood', '')
    category = request.args.get('category', '')
    favorites_only = request.args.get('favorites_only', False, type=bool)
    is_private = request.args.get('is_private', False, type=bool)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # Base query for user's diary entries
    entries_query = DiaryEntry.query.filter_by(user_id=current_user.id)

    # Apply filters
    if query:
        entries_query = entries_query.filter(or_(
            DiaryEntry.title.ilike(f'%{query}%'),
            DiaryEntry.content.ilike(f'%{query}%')
        ))

    if mood:
        entries_query = entries_query.filter_by(mood=mood)

    if category:
        entries_query = entries_query.filter_by(category=category)

    if favorites_only:
        entries_query = entries_query.filter_by(is_favorite=True)

    if is_private:
        entries_query = entries_query.filter_by(is_private=True)

    # Apply date range filter
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            entries_query = entries_query.filter(DiaryEntry.created_at >= from_date)
        except ValueError:
            flash("Invalid from date format. Please use YYYY-MM-DD format.", "warning")

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            # Add 1 day to include the end date fully
            to_date = to_date + timedelta(days=1)
            entries_query = entries_query.filter(DiaryEntry.created_at < to_date)
        except ValueError:
            flash("Invalid to date format. Please use YYYY-MM-DD format.", "warning")

    # Order by most recent first
    entries_query = entries_query.order_by(desc(DiaryEntry.created_at))

    # Paginate results
    entries_pagination = entries_query.paginate(page=page, per_page=per_page)
    entries = entries_pagination.items

    # Gather stats for sidebar - use more efficient SQL with aggregation
    # This makes a single query instead of several
    stats = get_diary_stats(current_user.id)

    # New entry form
    form = DiaryEntryForm()

    return render_template("diary/diary.html",
                           title="Diary",
                           entries=entries,
                           pagination=entries_pagination,
                           stats=stats,
                           form=form,
                           search_form=search_form)


def get_diary_stats(user_id):
    """Get comprehensive stats for the diary sidebar"""
    # Basic counts
    total_entries = DiaryEntry.query.filter_by(user_id=user_id).count()
    favorites = DiaryEntry.query.filter_by(user_id=user_id, is_favorite=True).count()
    private_entries = DiaryEntry.query.filter_by(user_id=user_id, is_private=True).count()

    # Current month entries
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    this_month = DiaryEntry.query.filter(
        DiaryEntry.user_id == user_id,
        extract('month', DiaryEntry.created_at) == current_month,
        extract('year', DiaryEntry.created_at) == current_year
    ).count()

    # Categories and moods - more efficient query
    categories = db.session.query(
        DiaryEntry.category,
        func.count(DiaryEntry.id)
    ).filter(
        DiaryEntry.user_id == user_id,
        DiaryEntry.category != None,
        DiaryEntry.category != ''
    ).group_by(DiaryEntry.category).all()

    moods = db.session.query(
        DiaryEntry.mood,
        func.count(DiaryEntry.id)
    ).filter(
        DiaryEntry.user_id == user_id,
        DiaryEntry.mood != None,
        DiaryEntry.mood != ''
    ).group_by(DiaryEntry.mood).all()

    return {
        'total_entries': total_entries,
        'favorites': favorites,
        'private_entries': private_entries,
        'this_month': this_month,
        'categories': categories,
        'moods': moods
    }


@diary_bp.route("/diary/create", methods=["GET", "POST"])
@login_required
def create_entry():
    """Create a new diary entry"""
    if request.method == "GET":
        form = DiaryEntryForm()
        return render_template("diary/create_entry.html",
                               title="New Diary Entry",
                               form=form)

    form = DiaryEntryForm()

    if form.validate_on_submit():
        try:
            # Create new entry
            entry = DiaryEntry(
                title=form.title.data,
                content=form.content.data,
                mood=form.mood.data,
                category=form.category.data,
                is_favorite=form.is_favorite.data,
                is_private=form.is_private.data,
                weather=form.weather.data,
                location=form.location.data,
                user_id=current_user.id
            )

            db.session.add(entry)
            db.session.commit()

            flash("Diary entry created successfully!", "success")
            return redirect(url_for("diary.view_entry", entry_id=entry.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating diary entry: {str(e)}", "danger")

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return render_template("diary/create_entry.html",
                           title="New Diary Entry",
                           form=form)


@diary_bp.route("/diary/<int:entry_id>")
@login_required
def view_entry(entry_id):
    """View a specific diary entry"""
    entry = DiaryEntry.query.get_or_404(entry_id)

    # Ensure the entry belongs to the current user
    if entry.user_id != current_user.id:
        abort(403)  # Forbidden

    # Get next and previous entries for navigation
    next_entry = DiaryEntry.query.filter(
        DiaryEntry.user_id == current_user.id,
        DiaryEntry.created_at < entry.created_at
    ).order_by(DiaryEntry.created_at.desc()).first()

    prev_entry = DiaryEntry.query.filter(
        DiaryEntry.user_id == current_user.id,
        DiaryEntry.created_at > entry.created_at
    ).order_by(DiaryEntry.created_at.asc()).first()

    return render_template("diary/view_entry.html",
                           title=entry.title,
                           entry=entry,
                           next_entry=next_entry,
                           prev_entry=prev_entry)


@diary_bp.route("/diary/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    """Edit a diary entry"""
    entry = DiaryEntry.query.get_or_404(entry_id)

    # Ensure the entry belongs to the current user
    if entry.user_id != current_user.id:
        abort(403)  # Forbidden

    if request.method == "GET":
        form = DiaryEntryForm(obj=entry)
        return render_template("diary/edit_entry.html",
                               title=f"Edit: {entry.title}",
                               form=form,
                               entry=entry)

    form = DiaryEntryForm()

    if form.validate_on_submit():
        try:
            # Update entry fields
            entry.title = form.title.data
            entry.content = form.content.data
            entry.mood = form.mood.data
            entry.category = form.category.data
            entry.is_favorite = form.is_favorite.data
            entry.is_private = form.is_private.data
            entry.weather = form.weather.data
            entry.location = form.location.data

            db.session.commit()
            flash("Diary entry updated successfully!", "success")
            return redirect(url_for("diary.view_entry", entry_id=entry.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating diary entry: {str(e)}", "danger")

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return render_template("diary/edit_entry.html",
                           title=f"Edit: {entry.title}",
                           form=form,
                           entry=entry)


@diary_bp.route("/diary/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_entry(entry_id):
    """Delete a diary entry"""
    entry = DiaryEntry.query.get_or_404(entry_id)

    # Ensure the entry belongs to the current user
    if entry.user_id != current_user.id:
        abort(403)  # Forbidden

    try:
        db.session.delete(entry)
        db.session.commit()
        flash("Diary entry deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting diary entry: {str(e)}", "danger")

    return redirect(url_for("diary.diary"))


@diary_bp.route("/diary/<int:entry_id>/toggle-favorite", methods=["POST"])
@login_required
def toggle_favorite(entry_id):
    """Toggle favorite status of a diary entry"""
    entry = DiaryEntry.query.get_or_404(entry_id)

    # Ensure the entry belongs to the current user
    if entry.user_id != current_user.id:
        return jsonify({"success": False, "message": "Access denied"}), 403

    try:
        entry.is_favorite = not entry.is_favorite
        db.session.commit()

        status = "added to" if entry.is_favorite else "removed from"
        message = f"Entry {status} favorites"

        return jsonify({
            "success": True,
            "is_favorite": entry.is_favorite,
            "message": message
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@diary_bp.route("/diary/favorites")
@login_required
def favorites():
    """View favorite diary entries"""
    entries = DiaryEntry.query.filter_by(
        user_id=current_user.id,
        is_favorite=True
    ).order_by(desc(DiaryEntry.created_at)).all()

    return render_template("diary/favorites.html",
                           title="Favorite Entries",
                           entries=entries)


@diary_bp.route("/diary/categories/<category>")
@login_required
def category_entries(category):
    """View entries by category"""
    entries = DiaryEntry.query.filter_by(
        user_id=current_user.id,
        category=category
    ).order_by(desc(DiaryEntry.created_at)).all()

    return render_template("diary/category.html",
                           title=f"Category: {category.capitalize()}",
                           category=category,
                           entries=entries)


@diary_bp.route("/diary/moods/<mood>")
@login_required
def mood_entries(mood):
    """View entries by mood"""
    entries = DiaryEntry.query.filter_by(
        user_id=current_user.id,
        mood=mood
    ).order_by(desc(DiaryEntry.created_at)).all()

    return render_template("diary/mood.html",
                           title=f"Mood: {mood.capitalize()}",
                           mood=mood,
                           entries=entries)


@diary_bp.route("/diary/statistics")
@login_required
def statistics():
    """View diary statistics and insights"""
    # Count entries by month
    monthly_counts = db.session.query(
        func.extract('year', DiaryEntry.created_at).label('year'),
        func.extract('month', DiaryEntry.created_at).label('month'),
        func.count(DiaryEntry.id).label('count')
    ).filter(
        DiaryEntry.user_id == current_user.id
    ).group_by('year', 'month').order_by('year', 'month').all()

    # Format the data for charting
    months_data = []
    counts_data = []

    for year, month, count in monthly_counts:
        # Format as "Jan 2023"
        date_str = f"{datetime(int(year), int(month), 1).strftime('%b %Y')}"
        months_data.append(date_str)
        counts_data.append(count)

    # Get category distribution
    categories = db.session.query(
        DiaryEntry.category,
        func.count(DiaryEntry.id).label('count')
    ).filter(
        DiaryEntry.user_id == current_user.id,
        DiaryEntry.category != None,
        DiaryEntry.category != ''
    ).group_by(DiaryEntry.category).all()

    # Get mood distribution
    moods = db.session.query(
        DiaryEntry.mood,
        func.count(DiaryEntry.id).label('count')
    ).filter(
        DiaryEntry.user_id == current_user.id,
        DiaryEntry.mood != None,
        DiaryEntry.mood != ''
    ).group_by(DiaryEntry.mood).all()

    # Calculate streaks
    entries_by_date = db.session.query(
        func.date(DiaryEntry.created_at).label('date'),
        func.count(DiaryEntry.id).label('count')
    ).filter(
        DiaryEntry.user_id == current_user.id
    ).group_by('date').order_by('date').all()

    # Calculate current and longest streaks
    current_streak, longest_streak = calculate_streaks(entries_by_date)

    # Calculate average words per entry
    avg_words = db.session.query(
        func.avg(func.length(DiaryEntry.content) / 5)  # Rough word count estimation
    ).filter(
        DiaryEntry.user_id == current_user.id
    ).scalar() or 0

    # Calculate entry and word count by weekday for writing patterns
    entries_by_weekday = db.session.query(
        func.extract('dow', DiaryEntry.created_at).label('weekday'),
        func.count(DiaryEntry.id).label('count'),
        func.sum(func.length(DiaryEntry.content) / 5).label('words')
    ).filter(
        DiaryEntry.user_id == current_user.id
    ).group_by('weekday').all()

    # Format weekday data
    weekday_map = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
                   4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
    weekday_data = [{'day': weekday_map.get(int(wd), 'Unknown'), 'count': int(count),
                     'avg_words': int(words / count) if count else 0}
                    for wd, count, words in entries_by_weekday]

    # Sort by day of week
    weekday_data.sort(key=lambda x: list(weekday_map.values()).index(x['day']))

    stats = {
        'total_entries': DiaryEntry.query.filter_by(user_id=current_user.id).count(),
        'total_words': int(avg_words * DiaryEntry.query.filter_by(user_id=current_user.id).count()),
        'avg_words': int(avg_words),
        'favorite_count': DiaryEntry.query.filter_by(user_id=current_user.id, is_favorite=True).count(),
        'private_count': DiaryEntry.query.filter_by(user_id=current_user.id, is_private=True).count(),
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'monthly_counts': monthly_counts,
        'months_data': months_data,
        'counts_data': counts_data,
        'categories': categories,
        'moods': moods,
        'weekday_data': weekday_data
    }

    return render_template("diary/statistics.html",
                           title="Diary Statistics",
                           stats=stats)


@diary_bp.route("/diary/export", methods=["GET"])
@login_required
def export_diary():
    """Export diary entries as CSV"""
    format_type = request.args.get('format', 'csv')

    if format_type not in ['csv', 'txt']:
        flash("Invalid export format.", "warning")
        return redirect(url_for("diary.diary"))

    # Filter parameters
    category = request.args.get('category', '')
    mood = request.args.get('mood', '')
    favorites_only = request.args.get('favorites_only', False, type=bool)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # Build query
    query = DiaryEntry.query.filter_by(user_id=current_user.id)

    if category:
        query = query.filter_by(category=category)
    if mood:
        query = query.filter_by(mood=mood)
    if favorites_only:
        query = query.filter_by(is_favorite=True)

    # Date range filters
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(DiaryEntry.created_at >= from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            to_date = to_date + timedelta(days=1)  # Include the entire day
            query = query.filter(DiaryEntry.created_at < to_date)
        except ValueError:
            pass

    # Get entries
    entries = query.order_by(DiaryEntry.created_at).all()

    if format_type == 'csv':
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['Date', 'Title', 'Content', 'Mood', 'Category', 'Location', 'Weather', 'Favorite', 'Private'])

        # Write entries
        for entry in entries:
            writer.writerow([
                entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                entry.title,
                entry.content,
                entry.mood or '',
                entry.category or '',
                entry.location or '',
                entry.weather or '',
                'Yes' if entry.is_favorite else 'No',
                'Yes' if entry.is_private else 'No'
            ])

        # Prepare response
        output.seek(0)
        filename = f"diary_export_{datetime.now().strftime('%Y%m%d')}.csv"

        # Create response
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    else:
        # Generate plain text
        output = io.StringIO()

        for entry in entries:
            output.write(f"Date: {entry.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.write(f"Title: {entry.title}\n")
            if entry.mood:
                output.write(f"Mood: {entry.mood}\n")
            if entry.category:
                output.write(f"Category: {entry.category}\n")
            if entry.location:
                output.write(f"Location: {entry.location}\n")
            if entry.weather:
                output.write(f"Weather: {entry.weather}\n")
            output.write(f"Favorite: {'Yes' if entry.is_favorite else 'No'}\n")
            output.write(f"Private: {'Yes' if entry.is_private else 'No'}\n")
            output.write("\nContent:\n")
            output.write(f"{entry.content}\n")
            output.write("\n" + "-" * 50 + "\n\n")

        # Prepare response
        output.seek(0)
        filename = f"diary_export_{datetime.now().strftime('%Y%m%d')}.txt"

        # Create response
        from flask import Response

        return Response(
            output.getvalue(),
            mimetype="text/plain",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )


def calculate_streaks(entries_by_date):
    """Calculate current and longest streaks more accurately"""
    if not entries_by_date:
        return 0, 0

    # Convert to list of dates
    dates = [entry.date for entry in entries_by_date]
    dates_set = set(dates)  # For faster lookups

    # Sort dates chronologically
    sorted_dates = sorted(dates)

    # Calculate current streak
    current_streak = 0
    today = datetime.utcnow().date()

    # Check if there's an entry today or yesterday to consider a current streak
    has_active_streak = False

    if today in dates_set:
        # Entry today - streak is active
        has_active_streak = True
        current_streak = 1
        check_date = today - timedelta(days=1)
    elif (today - timedelta(days=1)) in dates_set:
        # Entry yesterday - streak is still active
        has_active_streak = True
        current_streak = 1
        check_date = today - timedelta(days=2)
    else:
        # No recent entries - no active streak
        current_streak = 0

    # Count backwards from most recent entry if we have an active streak
    if has_active_streak:
        while check_date in dates_set:
            current_streak += 1
            check_date = check_date - timedelta(days=1)

    # Calculate longest streak
    if not sorted_dates:
        return current_streak, 0

    # Initialize variables for tracking streaks
    longest_streak = 1
    current_run = 1
    prev_date = sorted_dates[0]

    # Iterate through sorted dates
    for i in range(1, len(sorted_dates)):
        current_date = sorted_dates[i]
        days_diff = (current_date - prev_date).days

        if days_diff == 1:
            # Consecutive day, extend the current run
            current_run += 1
        elif days_diff > 1:
            # Gap detected, reset the streak
            longest_streak = max(longest_streak, current_run)
            current_run = 1

        prev_date = current_date

    # Check if the last streak is the longest
    longest_streak = max(longest_streak, current_run)

    return current_streak, longest_streak


@diary_bp.route("/diary/calendar")
@login_required
def diary_calendar():
    """View diary entries in a calendar format"""
    # Get month and year from query params
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    # Default to current month if not specified
    if not year or not month:
        today = datetime.utcnow()
        year = today.year
        month = today.month

    # Get all entries for this month
    start_date = datetime(year, month, 1)

    # Calculate end date (first day of next month)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    # Get entries for the month
    entries = DiaryEntry.query.filter(
        DiaryEntry.user_id == current_user.id,
        DiaryEntry.created_at >= start_date,
        DiaryEntry.created_at < end_date
    ).order_by(DiaryEntry.created_at).all()

    # Group entries by day
    entries_by_day = defaultdict(list)
    for entry in entries:
        day = entry.created_at.day
        entries_by_day[day].append(entry)

    # Calculate calendar data for UI rendering
    calendar_data = generate_calendar_data(year, month, entries_by_day)

    # Get the month name for display
    month_name = start_date.strftime('%B %Y')

    # Get previous and next month links
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1

    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    return render_template(
        "diary/calendar.html",
        title="Diary Calendar",
        year=year,
        month=month,
        month_name=month_name,
        calendar_data=calendar_data,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year
    )


def generate_calendar_data(year, month, entries_by_day):
    """Generate calendar data for the template"""
    import calendar

    # Create a calendar for the month
    cal = calendar.monthcalendar(year, month)

    # Enhance with entry data
    calendar_data = []

    for week in cal:
        week_data = []
        for day in week:
            if day == 0:  # Day is outside current month
                week_data.append({
                    'day': None,
                    'entries': [],
                    'today': False
                })
            else:
                # Check if this is today
                today = datetime.utcnow().date()
                is_today = (today.year == year and today.month == month and today.day == day)

                week_data.append({
                    'day': day,
                    'entries': entries_by_day[day],
                    'today': is_today
                })
        calendar_data.append(week_data)

    return calendar_data


@diary_bp.route("/diary/insights")
@login_required
def diary_insights():
    """Generate writing insights from diary entries"""
    # Get basic stats
    entry_count = DiaryEntry.query.filter_by(user_id=current_user.id).count()

    if entry_count == 0:
        flash("You need to write some entries before we can generate insights.", "info")
        return redirect(url_for("diary.diary"))

    # Time analysis
    time_analysis = db.session.query(
        func.extract('hour', DiaryEntry.created_at).label('hour'),
        func.count(DiaryEntry.id).label('count')
    ).filter(
        DiaryEntry.user_id == current_user.id
    ).group_by('hour').all()

    # Convert to a more usable format
    hours = [int(hour) for hour, _ in time_analysis]
    counts = [int(count) for _, count in time_analysis]

    # Find peak writing times
    if time_analysis:
        peak_hour = max(time_analysis, key=lambda x: x[1])
        peak_hour_formatted = f"{int(peak_hour[0]):02d}:00 - {int(peak_hour[0]) + 1:02d}:00"
    else:
        peak_hour_formatted = "N/A"

    # Word count analysis
    avg_entry_length = db.session.query(
        func.avg(func.length(DiaryEntry.content) / 5)  # Approximation for word count
    ).filter(
        DiaryEntry.user_id == current_user.id
    ).scalar() or 0

    # Most written about topics (based on categories)
    top_categories = db.session.query(
        DiaryEntry.category,
        func.count(DiaryEntry.id).label('count')
    ).filter(
        DiaryEntry.user_id == current_user.id,
        DiaryEntry.category != None,
        DiaryEntry.category != ''
    ).group_by(DiaryEntry.category).order_by(desc('count')).limit(3).all()

    # Most common moods
    top_moods = db.session.query(
        DiaryEntry.mood,
        func.count(DiaryEntry.id).label('count')
    ).filter(
        DiaryEntry.user_id == current_user.id,
        DiaryEntry.mood != None,
        DiaryEntry.mood != ''
    ).group_by(DiaryEntry.mood).order_by(desc('count')).limit(3).all()

    # Create consistency score (0-100)
    # Based on frequency, average word count, and streak factors
    streak_data = calculate_streaks(db.session.query(
        func.date(DiaryEntry.created_at).label('date'),
        func.count(DiaryEntry.id).label('count')
    ).filter(
        DiaryEntry.user_id == current_user.id
    ).group_by('date').all())

    current_streak, longest_streak = streak_data

    # Weekly frequency
    weekly_frequency = db.session.query(
        func.count(func.distinct(func.date(DiaryEntry.created_at)))
    ).filter(
        DiaryEntry.user_id == current_user.id,
        DiaryEntry.created_at >= datetime.utcnow() - timedelta(days=30)
    ).scalar() or 0

    # Normalize to per week
    weekly_frequency = (weekly_frequency / 30) * 7

    # Calculate consistency score components
    frequency_score = min(100, weekly_frequency * 20)  # 5 days a week = 100
    streak_score = min(100, longest_streak * 10)  # 10 day streak = 100
    length_score = min(100, avg_entry_length / 3)  # 300 words = 100

    consistency_score = int((frequency_score + streak_score + length_score) / 3)

    # Month-over-month growth
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    if current_month == 1:
        prev_month = 12
        prev_year = current_year - 1
    else:
        prev_month = current_month - 1
        prev_year = current_year

    current_month_count = DiaryEntry.query.filter(
        DiaryEntry.user_id == current_user.id,
        extract('month', DiaryEntry.created_at) == current_month,
        extract('year', DiaryEntry.created_at) == current_year
    ).count()

    prev_month_count = DiaryEntry.query.filter(
        DiaryEntry.user_id == current_user.id,
        extract('month', DiaryEntry.created_at) == prev_month,
        extract('year', DiaryEntry.created_at) == prev_year
    ).count()

    if prev_month_count > 0:
        growth_percentage = ((current_month_count - prev_month_count) / prev_month_count) * 100
    else:
        growth_percentage = 0

    insights = {
        'entry_count': entry_count,
        'peak_writing_time': peak_hour_formatted,
        'time_data': {
            'hours': hours,
            'counts': counts
        },
        'avg_entry_length': int(avg_entry_length),
        'top_categories': top_categories,
        'top_moods': top_moods,
        'consistency_score': consistency_score,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'current_month_count': current_month_count,
        'prev_month_count': prev_month_count,
        'growth_percentage': growth_percentage
    }

    return render_template("diary/insights.html",
                           title="Diary Insights",
                           insights=insights)
