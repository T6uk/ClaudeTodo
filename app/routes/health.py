"""
Health routes for workout and meal tracking
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import func, extract, cast, Date

from app import db
from app.models.workout import Workout
from app.models.meal import Meal
from app.models.body_metrics import BodyMetrics
from app.models.water_intake import WaterIntake
from app.forms.health_forms import WorkoutForm, MealForm, BodyMetricsForm, WaterIntakeForm

health_bp = Blueprint("health", __name__)

@health_bp.route("/health")
@login_required
def health():
    """Health dashboard with tabs for workouts, meals, and body metrics"""
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

    # Get body metrics
    metrics = BodyMetrics.query.filter(
        BodyMetrics.user_id == current_user.id,
        BodyMetrics.date >= start_date,
        BodyMetrics.date <= end_date
    ).order_by(BodyMetrics.date.desc()).all()

    # Get water intake for today
    today = datetime.utcnow().date()
    water_today = WaterIntake.query.filter(
        WaterIntake.user_id == current_user.id,
        cast(WaterIntake.date, Date) == today
    ).all()

    # Calculate total water intake for today
    total_water_today = sum(intake.amount for intake in water_today)

    # Get the latest body metrics for the user
    latest_metrics = BodyMetrics.query.filter_by(
        user_id=current_user.id
    ).order_by(BodyMetrics.date.desc()).first()

    # Calculate workout statistics
    workout_stats = {
        'total_workouts': len(workouts),
        'total_duration': sum(w.duration for w in workouts),
        'avg_duration': round(sum(w.duration for w in workouts) / len(workouts), 1) if workouts else 0,
        'total_calories': sum(w.calories_burned for w in workouts if w.calories_burned is not None),
        'by_type': {},
        'streak': calculate_workout_streak(current_user.id)
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

    # Create forms for adding data
    workout_form = WorkoutForm()
    meal_form = MealForm()
    metrics_form = BodyMetricsForm()
    water_form = WaterIntakeForm()

    # Set default dates to now
    workout_form.date.data = datetime.utcnow()
    meal_form.meal_time.data = datetime.utcnow()
    metrics_form.date.data = datetime.utcnow()
    water_form.date.data = datetime.utcnow()

    # Prefill metrics form with latest data if available
    if latest_metrics:
        metrics_form.weight.data = latest_metrics.weight
        metrics_form.height.data = latest_metrics.height

    # Get daily workout data for past 14 days for chart
    today = datetime.utcnow().date()
    workout_dates = []
    workout_durations = []

    for i in range(13, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        # Get total workout minutes for this date
        day_workouts = [w for w in workouts if w.date.date() == date]
        total_minutes = sum(w.duration for w in day_workouts)

        workout_dates.append(date.strftime('%b %d'))
        workout_durations.append(total_minutes)

    # Get daily calorie data for chart
    calorie_dates = []
    calorie_data = []

    for i in range(13, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')

        # Get total calories for this date
        day_meals = [m for m in meals if m.meal_time.date() == date]
        total_calories = sum(m.calories for m in day_meals if m.calories is not None)

        calorie_dates.append(date.strftime('%b %d'))
        calorie_data.append(total_calories)

    # Get metrics data for chart
    metrics_dates = []
    weights = []

    # Only include metrics with weight data
    weight_metrics = [m for m in metrics if m.weight is not None]
    sorted_metrics = sorted(weight_metrics, key=lambda m: m.date)

    for metric in sorted_metrics[-10:]:  # Last 10 measurements
        metrics_dates.append(metric.date.strftime('%b %d'))
        weights.append(metric.weight)

    return render_template("health/health.html",
                          title="Health Tracking",
                          workouts=workouts,
                          meals=meals,
                          metrics=metrics,
                          latest_metrics=latest_metrics,
                          total_water_today=total_water_today,
                          water_intakes=water_today,
                          workout_stats=workout_stats,
                          nutrition_stats=nutrition_stats,
                          workout_form=workout_form,
                          meal_form=meal_form,
                          metrics_form=metrics_form,
                          water_form=water_form,
                          workout_dates=workout_dates,
                          workout_durations=workout_durations,
                          calorie_dates=calorie_dates,
                          calorie_data=calorie_data,
                          metrics_dates=metrics_dates,
                          weights=weights)

def calculate_workout_streak(user_id):
    """Calculate the current workout streak for a user"""
    # Get all workout dates for the user, ordered by date descending
    workout_dates = db.session.query(
        cast(Workout.date, Date)
    ).filter(
        Workout.user_id == user_id
    ).distinct().order_by(
        cast(Workout.date, Date).desc()
    ).all()

    if not workout_dates:
        return 0

    # Extract dates and convert to list of date objects
    dates = [date[0] for date in workout_dates]

    # Check if there's a workout today
    today = datetime.utcnow().date()
    streak = 1 if today in dates else 0

    # Start from yesterday and go backwards
    check_date = today - timedelta(days=1)

    while check_date in dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak

# Existing workout routes (create, get, update, delete) remain unchanged...

@health_bp.route("/health/body-metrics/create", methods=["POST"])
@login_required
def create_metrics():
    """Create a new body metrics record"""
    form = BodyMetricsForm()

    if form.validate_on_submit():
        # Create metrics entry
        metrics = BodyMetrics(
            user_id=current_user.id,
            date=form.date.data,
            weight=form.weight.data,
            height=form.height.data,
            body_fat=form.body_fat.data,
            waist=form.waist.data,
            chest=form.chest.data,
            arms=form.arms.data,
            thighs=form.thighs.data,
            notes=form.notes.data
        )

        db.session.add(metrics)
        db.session.commit()

        flash("Body measurements saved successfully!", "success")
        return redirect(url_for("health.health"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/body-metrics/<int:metrics_id>")
@login_required
def get_metrics(metrics_id):
    """Get body metrics details"""
    metrics = BodyMetrics.query.get_or_404(metrics_id)

    # Ensure the metrics belong to the current user
    if metrics.user_id != current_user.id:
        flash("You don't have permission to view these measurements.", "danger")
        return redirect(url_for("health.health"))

    return jsonify(metrics.to_dict())

@health_bp.route("/health/body-metrics/<int:metrics_id>/update", methods=["POST"])
@login_required
def update_metrics(metrics_id):
    """Update body metrics"""
    metrics = BodyMetrics.query.get_or_404(metrics_id)

    # Ensure the metrics belong to the current user
    if metrics.user_id != current_user.id:
        flash("You don't have permission to update these measurements.", "danger")
        return redirect(url_for("health.health"))

    form = BodyMetricsForm()

    if form.validate_on_submit():
        # Update metrics
        metrics.date = form.date.data
        metrics.weight = form.weight.data
        metrics.height = form.height.data
        metrics.body_fat = form.body_fat.data
        metrics.waist = form.waist.data
        metrics.chest = form.chest.data
        metrics.arms = form.arms.data
        metrics.thighs = form.thighs.data
        metrics.notes = form.notes.data

        # Recalculate BMI if weight and height are provided
        if form.weight.data and form.height.data and form.height.data > 0:
            metrics.bmi = form.weight.data / ((form.height.data / 100) ** 2)
        else:
            metrics.bmi = None

        db.session.commit()
        flash("Measurements updated successfully!", "success")
        return redirect(url_for("health.health"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/body-metrics/<int:metrics_id>/delete", methods=["POST"])
@login_required
def delete_metrics(metrics_id):
    """Delete body metrics record"""
    metrics = BodyMetrics.query.get_or_404(metrics_id)

    # Ensure the metrics belong to the current user
    if metrics.user_id != current_user.id:
        flash("You don't have permission to delete these measurements.", "danger")
        return redirect(url_for("health.health"))

    db.session.delete(metrics)
    db.session.commit()

    flash("Measurements deleted successfully!", "success")
    return redirect(url_for("health.health"))

@health_bp.route("/health/water/add", methods=["POST"])
@login_required
def add_water():
    """Add water intake record"""
    form = WaterIntakeForm()

    if form.validate_on_submit():
        water = WaterIntake(
            user_id=current_user.id,
            amount=form.amount.data,
            date=form.date.data
        )

        db.session.add(water)
        db.session.commit()

        flash("Water intake recorded successfully!", "success")
        return redirect(url_for("health.health"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/water/<int:water_id>/delete", methods=["POST"])
@login_required
def delete_water(water_id):
    """Delete water intake record"""
    water = WaterIntake.query.get_or_404(water_id)

    # Ensure the water intake record belongs to the current user
    if water.user_id != current_user.id:
        flash("You don't have permission to delete this record.", "danger")
        return redirect(url_for("health.health"))

    db.session.delete(water)
    db.session.commit()

    flash("Water intake record deleted successfully!", "success")
    return redirect(url_for("health.health"))

@health_bp.route("/health/reports/weekly")
@login_required
def weekly_report():
    """Generate a weekly health report"""
    # Get end date (today)
    end_date = datetime.utcnow()
    # Get start date (7 days ago)
    start_date = end_date - timedelta(days=7)

    # Get workouts for the past week
    workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.date >= start_date,
        Workout.date <= end_date
    ).all()

    # Get meals for the past week
    meals = Meal.query.filter(
        Meal.user_id == current_user.id,
        Meal.meal_time >= start_date,
        Meal.meal_time <= end_date
    ).all()

    # Calculate workout stats
    workout_minutes = sum(w.duration for w in workouts)
    workout_calories = sum(w.calories_burned for w in workouts if w.calories_burned is not None)

    # Calculate nutrition stats
    total_calories = sum(m.calories for m in meals if m.calories is not None)
    avg_daily_calories = total_calories / 7 if meals else 0
    total_protein = sum(m.protein for m in meals if m.protein is not None)
    total_carbs = sum(m.carbs for m in meals if m.carbs is not None)
    total_fat = sum(m.fat for m in meals if m.fat is not None)

    # Get weight change
    start_weight = BodyMetrics.query.filter(
        BodyMetrics.user_id == current_user.id,
        BodyMetrics.date <= start_date,
        BodyMetrics.weight.isnot(None)
    ).order_by(BodyMetrics.date.desc()).first()

    end_weight = BodyMetrics.query.filter(
        BodyMetrics.user_id == current_user.id,
        BodyMetrics.date <= end_date,
        BodyMetrics.weight.isnot(None)
    ).order_by(BodyMetrics.date.desc()).first()

    weight_change = None
    if start_weight and end_weight:
        weight_change = end_weight.weight - start_weight.weight

    report = {
        'start_date': start_date,
        'end_date': end_date,
        'workouts': {
            'count': len(workouts),
            'minutes': workout_minutes,
            'calories': workout_calories
        },
        'nutrition': {
            'meals': len(meals),
            'total_calories': total_calories,
            'avg_daily_calories': avg_daily_calories,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat
        },
        'weight_change': weight_change
    }

    return render_template("health/report.html",
                          title="Weekly Health Report",
                          report=report,
                          workouts=workouts,
                          meals=meals)