"""
Diary routes for personal journal entries
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import current_user, login_required
from datetime import datetime
from sqlalchemy import desc, or_, func

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

    # Order by most recent first
    entries_query = entries_query.order_by(desc(DiaryEntry.created_at))

    # Paginate results
    entries_pagination = entries_query.paginate(page=page, per_page=per_page)
    entries = entries_pagination.items

    # Gather stats for sidebar
    stats = {
        'total_entries': DiaryEntry.query.filter_by(user_id=current_user.id).count(),
        'favorites': DiaryEntry.query.filter_by(user_id=current_user.id, is_favorite=True).count(),
        'private_entries': DiaryEntry.query.filter_by(user_id=current_user.id, is_private=True).count(),
        'this_month': DiaryEntry.query.filter(
            DiaryEntry.user_id == current_user.id,
            func.extract('month', DiaryEntry.created_at) == datetime.utcnow().month,
            func.extract('year', DiaryEntry.created_at) == datetime.utcnow().year
        ).count(),
        'categories': db.session.query(
            DiaryEntry.category,
            func.count(DiaryEntry.id)
        ).filter(
            DiaryEntry.user_id == current_user.id,
            DiaryEntry.category != None,
            DiaryEntry.category != ''
        ).group_by(DiaryEntry.category).all(),
        'moods': db.session.query(
            DiaryEntry.mood,
            func.count(DiaryEntry.id)
        ).filter(
            DiaryEntry.user_id == current_user.id,
            DiaryEntry.mood != None,
            DiaryEntry.mood != ''
        ).group_by(DiaryEntry.mood).all()
    }

    # New entry form
    form = DiaryEntryForm()

    return render_template("diary/diary.html",
                           title="Diary",
                           entries=entries,
                           pagination=entries_pagination,
                           stats=stats,
                           form=form,
                           search_form=search_form)


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

    return redirect(url_for("diary.diary"))


@diary_bp.route("/diary/<int:entry_id>")
@login_required
def view_entry(entry_id):
    """View a specific diary entry"""
    entry = DiaryEntry.query.get_or_404(entry_id)

    # Ensure the entry belongs to the current user
    if entry.user_id != current_user.id:
        abort(403)  # Forbidden

    return render_template("diary/view_entry.html",
                           title=entry.title,
                           entry=entry)


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

    return redirect(url_for("diary.view_entry", entry_id=entry.id))


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
        'moods': moods
    }

    return render_template("diary/statistics.html",
                           title="Diary Statistics",
                           stats=stats)


def calculate_streaks(entries_by_date):
    """Calculate current and longest streaks"""
    if not entries_by_date:
        return 0, 0

    # Convert to list of dates
    dates = [entry.date for entry in entries_by_date]

    # Calculate current streak
    current_streak = 0
    today = datetime.utcnow().date()

    # Check if there's an entry today
    if today in dates:
        current_streak = 1
        check_date = today

        while True:
            # Check previous day
            check_date = check_date - db.func.timedelta(days=1)
            if check_date in dates:
                current_streak += 1
            else:
                break

    # Calculate longest streak
    longest_streak = 0
    current = 0

    for i in range(len(dates)):
        # If this is the first entry or consecutive day
        if i == 0 or (dates[i] - dates[i - 1]).days == 1:
            current += 1
        else:
            current = 1  # Reset streak

        longest_streak = max(longest_streak, current)

    return current_streak, longest_streak