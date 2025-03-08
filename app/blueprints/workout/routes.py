from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Workout, Exercise
from app.blueprints.workout import workout_bp
from app.blueprints.workout.forms import WorkoutForm, ExerciseForm


@workout_bp.route('/')
@login_required
def list_workouts():
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
    return render_template('workout/list.html', title='My Workouts', workouts=workouts)


@workout_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_workout():
    form = WorkoutForm()
    if form.validate_on_submit():
        workout = Workout(
            workout_type=form.workout_type.data,
            duration=form.duration.data,
            calories_burned=form.calories_burned.data,
            notes=form.notes.data,
            date=form.date.data,
            user_id=current_user.id
        )
        db.session.add(workout)
        db.session.commit()
        flash('Workout created successfully!', 'success')
        return redirect(url_for('workout.edit_exercises', workout_id=workout.id))

    return render_template('workout/workout.html', title='New Workout', form=form, is_update=False)


@workout_bp.route('/<int:workout_id>', methods=['GET'])
@login_required
def view_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the current user owns this workout
    if workout.user_id != current_user.id:
        abort(403)

    return render_template('workout/view.html', title=f'{workout.workout_type} Workout', workout=workout)


@workout_bp.route('/<int:workout_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the current user owns this workout
    if workout.user_id != current_user.id:
        abort(403)

    form = WorkoutForm()

    if form.validate_on_submit():
        workout.workout_type = form.workout_type.data
        workout.duration = form.duration.data
        workout.calories_burned = form.calories_burned.data
        workout.notes = form.notes.data
        workout.date = form.date.data
        db.session.commit()
        flash('Workout updated successfully!', 'success')
        return redirect(url_for('workout.view_workout', workout_id=workout.id))

    # Pre-fill the form with current data
    if request.method == 'GET':
        form.workout_type.data = workout.workout_type
        form.duration.data = workout.duration
        form.calories_burned.data = workout.calories_burned
        form.notes.data = workout.notes
        form.date.data = workout.date

    return render_template('workout/workout.html', title='Edit Workout', form=form, is_update=True)


@workout_bp.route('/<int:workout_id>/exercises', methods=['GET', 'POST'])
@login_required
def edit_exercises(workout_id):
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the current user owns this workout
    if workout.user_id != current_user.id:
        abort(403)

    form = ExerciseForm()

    if form.validate_on_submit():
        exercise = Exercise(
            name=form.name.data,
            sets=form.sets.data,
            reps=form.reps.data,
            weight=form.weight.data,
            workout_id=workout.id
        )
        db.session.add(exercise)
        db.session.commit()
        flash('Exercise added successfully!', 'success')
        return redirect(url_for('workout.edit_exercises', workout_id=workout.id))

    exercises = Exercise.query.filter_by(workout_id=workout.id).all()

    return render_template(
        'workout/exercises.html',
        title='Edit Exercises',
        form=form,
        workout=workout,
        exercises=exercises
    )


@workout_bp.route('/<int:workout_id>/exercises/<int:exercise_id>/delete', methods=['POST'])
@login_required
def delete_exercise(workout_id, exercise_id):
    workout = Workout.query.get_or_404(workout_id)
    exercise = Exercise.query.get_or_404(exercise_id)

    # Ensure the current user owns this workout and the exercise belongs to the workout
    if workout.user_id != current_user.id or exercise.workout_id != workout.id:
        abort(403)

    db.session.delete(exercise)
    db.session.commit()
    flash('Exercise deleted successfully!', 'success')
    return redirect(url_for('workout.edit_exercises', workout_id=workout.id))


@workout_bp.route('/<int:workout_id>/delete', methods=['POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)

    # Ensure the current user owns this workout
    if workout.user_id != current_user.id:
        abort(403)

    # Delete all associated exercises first
    Exercise.query.filter_by(workout_id=workout.id).delete()

    db.session.delete(workout)
    db.session.commit()
    flash('Workout deleted successfully!', 'success')
    return redirect(url_for('workout.list_workouts'))