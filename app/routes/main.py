# app/routes/main.py (update)
"""
Main routes for the application
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from app.models.dashboard_widget import DashboardWidget

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/home")
def home():
    """
    Home page route
    If user is not authenticated, redirect to login page
    """
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return redirect(url_for("todo.todos"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard route - requires authentication"""
    # Get user's dashboard widgets
    widgets = DashboardWidget.query.filter_by(user_id=current_user.id).order_by(DashboardWidget.position).all()

    from datetime import datetime, timedelta
    from app.models.workout import Workout
    from app.models.meal import Meal
    from app.models.body_metrics import BodyMetrics
    from app.models.water_intake import WaterIntake
    from app.routes.health import calculate_workout_streak
    from sqlalchemy import func
    from app.models.diary import DiaryEntry  # Add this line

    # Default to showing data from the past 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    # Get workouts for the current user
    workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.date >= start_date,
        Workout.date <= end_date
    ).order_by(Workout.date.desc()).all()

    # Get meals for the current user
    meals = Meal.query.filter(
        Meal.user_id == current_user.id,
        Meal.meal_time >= start_date,
        Meal.meal_time <= end_date
    ).order_by(Meal.meal_time.desc()).all()

    # Get the latest body metrics for the user
    latest_metrics = BodyMetrics.query.filter_by(
        user_id=current_user.id
    ).order_by(BodyMetrics.date.desc()).first()

    # Get water intake for today
    today = datetime.utcnow().date()
    water_today = WaterIntake.query.filter(
        WaterIntake.user_id == current_user.id,
        func.date(WaterIntake.date) == today
    ).all()

    # Get recent diary entries
    diary_entries = DiaryEntry.query.filter_by(
        user_id=current_user.id
    ).order_by(DiaryEntry.created_at.desc()).limit(5).all()

    # Calculate total water intake for today
    total_water_today = sum(intake.amount for intake in water_today)

    # Calculate workout statistics
    workout_stats = {
        'total_workouts': len(workouts),
        'total_duration': sum(w.duration for w in workouts),
        'avg_duration': round(sum(w.duration for w in workouts) / len(workouts), 1) if workouts else 0,
        'total_calories': sum(w.calories_burned for w in workouts if w.calories_burned is not None),
        'by_type': {},
        'streak': calculate_workout_streak(current_user.id),
        'favorite_count': Workout.query.filter_by(user_id=current_user.id, favorite=True).count()
    }

    # Group workouts by type
    for workout in workouts:
        if workout.workout_type not in workout_stats['by_type']:
            workout_stats['by_type'][workout.workout_type] = 0
        workout_stats['by_type'][workout.workout_type] += 1

    # Calculate nutrition statistics
    nutrition_stats = {
        'total_meals': len(meals),
        'total_calories': sum(m.calories for m in meals if m.calories is not None),
        'avg_calories_per_day': round(sum(m.calories for m in meals if m.calories is not None) / 30, 1) if meals else 0,
        'total_protein': sum(m.protein for m in meals if m.protein is not None),
        'total_carbs': sum(m.carbs for m in meals if m.carbs is not None),
        'total_fat': sum(m.fat for m in meals if m.fat is not None),
        'by_meal_type': {}
    }

    # Group meals by type
    for meal in meals:
        if meal.name not in nutrition_stats['by_meal_type']:
            nutrition_stats['by_meal_type'][meal.name] = 0
        nutrition_stats['by_meal_type'][meal.name] += 1

    # Calculate water progress percentage
    water_percentage = min(100, (total_water_today / 2500) * 100) if total_water_today > 0 else 0

    return render_template("dashboard.html",
                           title="Dashboard",
                           widgets=widgets,
                           workouts=workouts,
                           meals=meals,
                           latest_metrics=latest_metrics,
                           total_water_today=total_water_today,
                           water_intakes=water_today,
                           workout_stats=workout_stats,
                           nutrition_stats=nutrition_stats,
                           water_percentage=water_percentage,
                           diary_entries=diary_entries)  # Add this line