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
from app.models.exercise import Exercise
from app.forms.health_forms import WorkoutForm, MealForm, BodyMetricsForm, WaterIntakeForm, ExerciseForm

health_bp = Blueprint("health", __name__)

def safe_iso_format(dt):
    """Safely convert a datetime to ISO format string"""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    try:
        return dt.isoformat()
    except AttributeError:
        return str(dt)

def safe_datetime_parse(dt_str):
    """Safely parse a datetime string to a datetime object"""
    if dt_str is None:
        return None
    if isinstance(dt_str, datetime):
        return dt_str
    try:
        # Handle different string formats
        if isinstance(dt_str, str):
            dt_str = dt_str.replace('Z', '+00:00')
            return datetime.fromisoformat(dt_str)
        return dt_str
    except (ValueError, AttributeError):
        # Fall back to datetime.utcnow if parsing fails
        return datetime.utcnow()

@health_bp.route("/health")
@login_required
def health():
    """Health dashboard with tabs for workouts, meals, and body metrics"""
    try:
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
            func.date(WaterIntake.date) == today  # Use func.date instead of cast
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

        # Create forms for adding data
        workout_form = WorkoutForm()
        meal_form = MealForm()
        metrics_form = BodyMetricsForm()
        water_form = WaterIntakeForm()

        # Set default dates to now
        current_time = datetime.utcnow()
        workout_form.date.data = current_time
        meal_form.meal_time.data = current_time
        metrics_form.date.data = current_time
        water_form.date.data = current_time

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
            date_str = date.strftime('%b %d')

            # Get total workout minutes for this date
            day_workouts = [w for w in workouts if w.date.date() == date]
            total_minutes = sum(w.duration for w in day_workouts)

            workout_dates.append(date_str)
            workout_durations.append(total_minutes)

        # Get daily calorie data for chart
        calorie_dates = []
        calorie_data = []

        for i in range(13, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%b %d')

            # Get total calories for this date
            day_meals = [m for m in meals if m.meal_time.date() == date]
            total_calories = sum(m.calories for m in day_meals if m.calories is not None)

            calorie_dates.append(date_str)
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

        # Calculate water progress percentage
        water_percentage = min(100, (total_water_today / 2500) * 100) if total_water_today > 0 else 0

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
                            weights=weights,
                            water_percentage=water_percentage)
    except Exception as e:
        # Log the error and redirect to dashboard
        flash(f"Error loading health dashboard: {str(e)}", "danger")
        return redirect(url_for("main.dashboard"))

def calculate_workout_streak(user_id):
    """Calculate the current workout streak for a user"""
    try:
        # Get all workout dates for the user, ordered by date descending
        # Use date() function for proper date conversion in the database
        workout_dates_query = db.session.query(
            func.date(Workout.date)  # Use func.date instead of cast to Date
        ).filter(
            Workout.user_id == user_id
        ).distinct().order_by(
            func.date(Workout.date).desc()
        )

        workout_dates = workout_dates_query.all()

        if not workout_dates:
            return 0

        # Extract dates and convert to list of date objects
        dates = []
        for date_row in workout_dates:
            if date_row[0] is not None:
                # Handle different types of date objects
                if isinstance(date_row[0], str):
                    try:
                        # Try to parse string to date
                        dates.append(datetime.strptime(date_row[0], '%Y-%m-%d').date())
                    except ValueError:
                        pass
                else:
                    # Already a date or datetime object
                    try:
                        if hasattr(date_row[0], 'date'):
                            # It's a datetime
                            dates.append(date_row[0].date())
                        else:
                            # It's already a date
                            dates.append(date_row[0])
                    except (AttributeError, TypeError):
                        pass

        if not dates:
            return 0

        # Check if there's a workout today
        today = datetime.utcnow().date()
        streak = 1 if today in dates else 0

        # Start from yesterday and go backwards
        check_date = today - timedelta(days=1)

        while check_date in dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak
    except Exception as e:
        # Log the error and return 0 as a fallback
        print(f"Error calculating workout streak: {str(e)}")
        return 0

@health_bp.route("/health/workouts/create", methods=["POST"])
@login_required
def create_workout():
    """Create a new workout"""
    form = WorkoutForm()

    if form.validate_on_submit():
        try:
            # Create new workout with safe date handling
            workout = Workout(
                title=form.title.data,
                workout_type=form.workout_type.data,
                duration=form.duration.data,
                intensity=form.intensity.data,
                calories_burned=form.calories_burned.data,
                notes=form.notes.data,
                date=safe_datetime_parse(form.date.data),
                user_id=current_user.id,
                completed=form.completed.data,
                favorite=form.favorite.data
            )

            db.session.add(workout)
            db.session.commit()

            flash("Workout logged successfully!", "success")

            # Redirect to exercise add page if the workout was just created
            return redirect(url_for("health.add_exercises", workout_id=workout.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving workout: {str(e)}", "danger")

        return redirect(url_for("health.health"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/workouts/<int:workout_id>")
@login_required
def get_workout(workout_id):
    """Get workout details"""
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the workout belongs to the current user
    if workout.user_id != current_user.id:
        flash("You don't have permission to view this workout.", "danger")
        return redirect(url_for("health.health"))

    # Create a dictionary with safely formatted dates
    workout_dict = workout.to_dict()

    return jsonify(workout_dict)

@health_bp.route("/health/workouts/<int:workout_id>/update", methods=["POST"])
@login_required
def update_workout(workout_id):
    """Update an existing workout"""
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the workout belongs to the current user
    if workout.user_id != current_user.id:
        flash("You don't have permission to update this workout.", "danger")
        return redirect(url_for("health.health"))

    form = WorkoutForm()

    if form.validate_on_submit():
        try:
            # Update workout fields with safe date handling
            workout.title = form.title.data
            workout.workout_type = form.workout_type.data
            workout.duration = form.duration.data
            workout.intensity = form.intensity.data
            workout.calories_burned = form.calories_burned.data
            workout.notes = form.notes.data
            workout.date = safe_datetime_parse(form.date.data)
            workout.completed = form.completed.data
            workout.favorite = form.favorite.data

            db.session.commit()
            flash("Workout updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating workout: {str(e)}", "danger")

        return redirect(url_for("health.health"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/workouts/<int:workout_id>/delete", methods=["POST"])
@login_required
def delete_workout(workout_id):
    """Delete a workout"""
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the workout belongs to the current user
    if workout.user_id != current_user.id:
        flash("You don't have permission to delete this workout.", "danger")
        return redirect(url_for("health.health"))

    try:
        db.session.delete(workout)
        db.session.commit()
        flash("Workout deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting workout: {str(e)}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/workouts/<int:workout_id>/exercises", methods=["GET", "POST"])
@login_required
def add_exercises(workout_id):
    """Add exercises to a workout"""
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the workout belongs to the current user
    if workout.user_id != current_user.id:
        flash("You don't have permission to modify this workout.", "danger")
        return redirect(url_for("health.health"))

    form = ExerciseForm()

    if request.method == "POST" and form.validate_on_submit():
        try:
            exercise = Exercise(
                name=form.name.data,
                sets=form.sets.data,
                reps=form.reps.data,
                weight=form.weight.data,
                duration=form.duration.data,
                distance=form.distance.data,
                notes=form.notes.data,
                workout_id=workout.id
            )

            db.session.add(exercise)
            db.session.commit()

            flash("Exercise added successfully!", "success")

            # Stay on the same page to add more exercises
            return redirect(url_for("health.add_exercises", workout_id=workout.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding exercise: {str(e)}", "danger")

    # Get existing exercises for this workout
    exercises = Exercise.query.filter_by(workout_id=workout.id).all()

    return render_template("health/add_exercises.html",
                          title=f"Add Exercises to {workout.title}",
                          workout=workout,
                          exercises=exercises,
                          form=form)

@health_bp.route("/health/exercises/<int:exercise_id>/delete", methods=["POST"])
@login_required
def delete_exercise(exercise_id):
    """Delete an exercise from a workout"""
    exercise = Exercise.query.get_or_404(exercise_id)
    workout_id = exercise.workout_id

    # Ensure the exercise belongs to a workout owned by the current user
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != current_user.id:
        flash("You don't have permission to modify this workout.", "danger")
        return redirect(url_for("health.health"))

    try:
        db.session.delete(exercise)
        db.session.commit()
        flash("Exercise deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting exercise: {str(e)}", "danger")

    return redirect(url_for("health.add_exercises", workout_id=workout_id))

@health_bp.route("/health/workouts/<int:workout_id>/complete", methods=["POST"])
@login_required
def complete_workout(workout_id):
    """Mark a workout as completed"""
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the workout belongs to the current user
    if workout.user_id != current_user.id:
        flash("You don't have permission to modify this workout.", "danger")
        return redirect(url_for("health.health"))

    try:
        workout.completed = True
        db.session.commit()
        flash("Workout marked as completed!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating workout: {str(e)}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/workouts/<int:workout_id>/toggle-favorite", methods=["POST"])
@login_required
def toggle_favorite(workout_id):
    """Toggle favorite status of a workout"""
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the workout belongs to the current user
    if workout.user_id != current_user.id:
        flash("You don't have permission to modify this workout.", "danger")
        return redirect(url_for("health.health"))

    try:
        workout.favorite = not workout.favorite
        db.session.commit()
        status = "added to" if workout.favorite else "removed from"
        flash(f"Workout {status} favorites!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating workout: {str(e)}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/workouts/favorites")
@login_required
def favorite_workouts():
    """Show favorite workouts"""
    favorite_workouts = Workout.query.filter_by(
        user_id=current_user.id,
        favorite=True
    ).order_by(Workout.date.desc()).all()

    workout_form = WorkoutForm()

    return render_template("health/favorites.html",
                          title="Favorite Workouts",
                          workouts=favorite_workouts,
                          workout_form=workout_form)

@health_bp.route("/health/template/create/<int:workout_id>", methods=["POST"])
@login_required
def create_template(workout_id):
    """Create a workout template from an existing workout"""
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the workout belongs to the current user
    if workout.user_id != current_user.id:
        flash("You don't have permission to use this workout.", "danger")
        return redirect(url_for("health.health"))

    try:
        # Create a new workout based on the existing one
        template = Workout(
            title=f"{workout.title} (Template)",
            workout_type=workout.workout_type,
            duration=workout.duration,
            intensity=workout.intensity,
            calories_burned=workout.calories_burned,
            notes=workout.notes,
            date=datetime.utcnow(),  # Set to current time
            user_id=current_user.id,
            completed=False,  # Templates are not completed
            favorite=True     # Auto-favorite templates
        )

        db.session.add(template)
        db.session.flush()  # Get the template ID without committing yet

        # Copy all exercises
        for exercise in workout.exercises:
            new_exercise = Exercise(
                name=exercise.name,
                sets=exercise.sets,
                reps=exercise.reps,
                weight=exercise.weight,
                duration=exercise.duration,
                distance=exercise.distance,
                notes=exercise.notes,
                workout_id=template.id
            )
            db.session.add(new_exercise)

        db.session.commit()
        flash("Workout template created and added to favorites!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating template: {str(e)}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/meals/create", methods=["POST"])
@login_required
def create_meal():
    """Create a new meal"""
    form = MealForm()

    if form.validate_on_submit():
        try:
            # Create new meal with safe date handling
            meal = Meal(
                name=form.name.data,
                food_items=form.food_items.data,
                calories=form.calories.data,
                protein=form.protein.data,
                carbs=form.carbs.data,
                fat=form.fat.data,
                meal_time=safe_datetime_parse(form.meal_time.data),
                notes=form.notes.data,
                user_id=current_user.id
            )

            db.session.add(meal)
            db.session.commit()

            flash("Meal logged successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving meal: {str(e)}", "danger")

        return redirect(url_for("health.health"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/meals/<int:meal_id>")
@login_required
def get_meal(meal_id):
    """Get meal details"""
    meal = Meal.query.get_or_404(meal_id)

    # Ensure the meal belongs to the current user
    if meal.user_id != current_user.id:
        flash("You don't have permission to view this meal.", "danger")
        return redirect(url_for("health.health"))

    # Use the to_dict method which safely formats dates
    return jsonify(meal.to_dict())

@health_bp.route("/health/meals/<int:meal_id>/update", methods=["POST"])
@login_required
def update_meal(meal_id):
    """Update an existing meal"""
    meal = Meal.query.get_or_404(meal_id)

    # Ensure the meal belongs to the current user
    if meal.user_id != current_user.id:
        flash("You don't have permission to update this meal.", "danger")
        return redirect(url_for("health.health"))

    form = MealForm()

    if form.validate_on_submit():
        try:
            # Update meal fields with safe date handling
            meal.name = form.name.data
            meal.food_items = form.food_items.data
            meal.calories = form.calories.data
            meal.protein = form.protein.data
            meal.carbs = form.carbs.data
            meal.fat = form.fat.data
            meal.meal_time = safe_datetime_parse(form.meal_time.data)
            meal.notes = form.notes.data

            db.session.commit()
            flash("Meal updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating meal: {str(e)}", "danger")

        return redirect(url_for("health.health"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/meals/<int:meal_id>/delete", methods=["POST"])
@login_required
def delete_meal(meal_id):
    """Delete a meal"""
    meal = Meal.query.get_or_404(meal_id)

    # Ensure the meal belongs to the current user
    if meal.user_id != current_user.id:
        flash("You don't have permission to delete this meal.", "danger")
        return redirect(url_for("health.health"))

    try:
        db.session.delete(meal)
        db.session.commit()
        flash("Meal deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting meal: {str(e)}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/body-metrics/create", methods=["POST"])
@login_required
def create_metrics():
    """Create a new body metrics record"""
    form = BodyMetricsForm()

    if form.validate_on_submit():
        try:
            # Create metrics entry with safe date handling
            metrics = BodyMetrics(
                user_id=current_user.id,
                date=safe_datetime_parse(form.date.data),
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
        except Exception as e:
            db.session.rollback()
            flash(f"Error saving measurements: {str(e)}", "danger")

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

    # Use the to_dict method which safely formats dates
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
        try:
            # Update metrics with safe date handling
            metrics.date = safe_datetime_parse(form.date.data)
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
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating measurements: {str(e)}", "danger")

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

    try:
        db.session.delete(metrics)
        db.session.commit()
        flash("Measurements deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting measurements: {str(e)}", "danger")

    return redirect(url_for("health.health"))

@health_bp.route("/health/water/add", methods=["POST"])
@login_required
def add_water():
    """Add water intake record"""
    form = WaterIntakeForm()

    if form.validate_on_submit():
        try:
            water = WaterIntake(
                user_id=current_user.id,
                amount=form.amount.data,
                date=safe_datetime_parse(form.date.data)
            )

            db.session.add(water)
            db.session.commit()

            flash("Water intake recorded successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error recording water intake: {str(e)}", "danger")

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

    try:
        db.session.delete(water)
        db.session.commit()
        flash("Water intake record deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting water intake record: {str(e)}", "danger")

    return redirect(url_for("health.health"))


@health_bp.route("/health/reports/weekly")
@login_required
def weekly_report():
    """Generate a weekly health report"""
    try:
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

        # Get exercise data
        total_exercises = 0
        exercise_counts = {}

        for workout in workouts:
            exercises = Exercise.query.filter_by(workout_id=workout.id).all()
            total_exercises += len(exercises)

            # Count exercise types
            for exercise in exercises:
                exercise_name = exercise.name.lower()
                if exercise_name in exercise_counts:
                    exercise_counts[exercise_name] += 1
                else:
                    exercise_counts[exercise_name] = 1

        # Get most common exercises
        top_exercises = sorted(exercise_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        report = {
            'start_date': start_date,
            'end_date': end_date,
            'workouts': {
                'count': len(workouts),
                'minutes': workout_minutes,
                'calories': workout_calories,
                'exercise_count': total_exercises,
                'top_exercises': top_exercises
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
    except Exception as e:
        flash(f"Error generating report: {str(e)}", "danger")
        return redirect(url_for("health.health"))


@health_bp.route("/health/exercises")
@login_required
def exercise_library():
    """View and manage exercise library"""
    # Get all unique exercises performed by the user
    exercises_query = db.session.query(
        Exercise.name,
        func.count(Exercise.id).label('count'),
        func.max(Exercise.created_at).label('last_used')
    ).filter(
        Exercise.workout_id.in_(
            db.session.query(Workout.id).filter_by(user_id=current_user.id)
        )
    ).group_by(Exercise.name).order_by(func.count(Exercise.id).desc())

    exercises = exercises_query.all()

    # Calculate statistics
    stats = {
        'total_unique': len(exercises),
        'total_performed': sum(ex.count for ex in exercises)
    }

    return render_template("health/exercise_library.html",
                           title="Exercise Library",
                           exercises=exercises,
                           stats=stats)


@health_bp.route("/health/workouts/export/<int:workout_id>")
@login_required
def export_workout(workout_id):
    """Export workout details to a printable format"""
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the workout belongs to the current user
    if workout.user_id != current_user.id:
        flash("You don't have permission to view this workout.", "danger")
        return redirect(url_for("health.health"))

    # Get exercises for this workout
    exercises = Exercise.query.filter_by(workout_id=workout.id).all()

    return render_template("health/export_workout.html",
                           title=f"Export: {workout.title}",
                           workout=workout,
                           exercises=exercises)


@health_bp.route("/health/analytics")
@login_required
def health_analytics():
    """Advanced health analytics dashboard"""
    # Set date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=90)  # Last 90 days

    # Get data
    workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.date >= start_date,
        Workout.date <= end_date
    ).order_by(Workout.date).all()

    meals = Meal.query.filter(
        Meal.user_id == current_user.id,
        Meal.meal_time >= start_date,
        Meal.meal_time <= end_date
    ).order_by(Meal.meal_time).all()

    metrics = BodyMetrics.query.filter(
        BodyMetrics.user_id == current_user.id,
        BodyMetrics.date >= start_date,
        BodyMetrics.date <= end_date
    ).order_by(BodyMetrics.date).all()

    # Calculate trend data for charts
    # Workout frequency by week
    weekly_workouts = {}
    for i in range(0, 13):  # Last 13 weeks
        week_start = end_date - timedelta(days=end_date.weekday(), weeks=i)
        week_end = week_start + timedelta(days=6)
        week_str = week_start.strftime('%b %d')

        weekly_count = Workout.query.filter(
            Workout.user_id == current_user.id,
            Workout.date >= week_start,
            Workout.date <= week_end
        ).count()

        weekly_workouts[week_str] = weekly_count

    # Workout minutes by type
    workout_minutes_by_type = {}
    for workout in workouts:
        if workout.workout_type not in workout_minutes_by_type:
            workout_minutes_by_type[workout.workout_type] = 0
        workout_minutes_by_type[workout.workout_type] += workout.duration

    # Calculate calorie balance
    calorie_balance = []
    for i in range(0, 30):  # Last 30 days
        day = end_date - timedelta(days=i)
        day_str = day.strftime('%b %d')

        day_meals = [m for m in meals if m.meal_time.date() == day.date()]
        day_workouts = [w for w in workouts if w.date.date() == day.date()]

        intake = sum(m.calories for m in day_meals if m.calories is not None)
        burned = sum(w.calories_burned for w in day_workouts if w.calories_burned is not None)

        calorie_balance.append({
            'date': day_str,
            'intake': intake,
            'burned': burned,
            'net': intake - burned
        })

    calorie_balance.reverse()  # Show oldest to newest

    # Workout progress over time
    progress_data = {}
    for workout_type in workout_minutes_by_type.keys():
        progress_data[workout_type] = []

        for i in range(0, 12):  # Last 12 weeks
            week_start = end_date - timedelta(days=end_date.weekday(), weeks=i)
            week_end = week_start + timedelta(days=6)
            week_str = week_start.strftime('%b %d')

            week_workouts = Workout.query.filter(
                Workout.user_id == current_user.id,
                Workout.workout_type == workout_type,
                Workout.date >= week_start,
                Workout.date <= week_end
            ).all()

            if week_workouts:
                total_duration = sum(w.duration for w in week_workouts)
                progress_data[workout_type].append({
                    'week': week_str,
                    'duration': total_duration
                })

    # Prepare data for templates
    chart_data = {
        'weekly_workouts': {
            'labels': list(weekly_workouts.keys()),
            'data': list(weekly_workouts.values())
        },
        'workout_by_type': {
            'labels': list(workout_minutes_by_type.keys()),
            'data': list(workout_minutes_by_type.values())
        },
        'calorie_balance': calorie_balance,
        'progress_data': progress_data
    }

    return render_template("health/analytics.html",
                           title="Health Analytics",
                           chart_data=chart_data,
                           workouts=workouts,
                           meals=meals,
                           metrics=metrics)


@health_bp.route("/health/goals")
@login_required
def health_goals():
    """Manage health and fitness goals"""
    # This would be expanded in a future version with a proper goals model
    return render_template("health/goals.html",
                           title="Health Goals")


@health_bp.route("/health/nutrition-calculator")
@login_required
def nutrition_calculator():
    """Nutrition calculator for meal planning"""
    # This would be expanded in a future version
    return render_template("health/nutrition_calculator.html",
                           title="Nutrition Calculator")