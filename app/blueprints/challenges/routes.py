from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from app import db
from app.models import Challenge
from app.blueprints.challenges import challenges_bp
from app.blueprints.challenges.forms import ChallengeForm, ProgressForm


@challenges_bp.route('/')
@login_required
def list_challenges():
    challenges = Challenge.query.filter_by(user_id=current_user.id).order_by(Challenge.end_date.asc()).all()
    return render_template('challenges/list.html', title='My Challenges', challenges=challenges)


@challenges_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_challenge():
    form = ChallengeForm()
    if form.validate_on_submit():
        challenge = Challenge(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            goal=form.goal.data,
            user_id=current_user.id
        )
        db.session.add(challenge)
        db.session.commit()
        flash('Challenge created successfully!', 'success')
        return redirect(url_for('challenges.list_challenges'))

    return render_template('challenges/challenge.html', title='New Challenge', form=form, is_update=False)


@challenges_bp.route('/<int:challenge_id>', methods=['GET', 'POST'])
@login_required
def view_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)

    # Ensure the current user owns this challenge
    if challenge.user_id != current_user.id:
        abort(403)

    progress_form = ProgressForm()

    if progress_form.validate_on_submit():
        challenge.progress = progress_form.progress.data
        challenge.completed = progress_form.progress.data >= 100
        db.session.commit()
        flash('Progress updated!', 'success')
        return redirect(url_for('challenges.view_challenge', challenge_id=challenge.id))

    # Pre-fill the form with current data
    if request.method == 'GET':
        progress_form.progress.data = challenge.progress

    return render_template('challenges/view.html', title=challenge.title, challenge=challenge, form=progress_form)


@challenges_bp.route('/<int:challenge_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)

    # Ensure the current user owns this challenge
    if challenge.user_id != current_user.id:
        abort(403)

    form = ChallengeForm()

    if form.validate_on_submit():
        challenge.title = form.title.data
        challenge.description = form.description.data
        challenge.start_date = form.start_date.data
        challenge.end_date = form.end_date.data
        challenge.goal = form.goal.data
        db.session.commit()
        flash('Challenge updated successfully!', 'success')
        return redirect(url_for('challenges.view_challenge', challenge_id=challenge.id))

    # Pre-fill the form with current data
    if request.method == 'GET':
        form.title.data = challenge.title
        form.description.data = challenge.description
        form.start_date.data = challenge.start_date
        form.end_date.data = challenge.end_date
        form.goal.data = challenge.goal

    return render_template('challenges/challenge.html', title='Edit Challenge', form=form, is_update=True)


@challenges_bp.route('/<int:challenge_id>/delete', methods=['POST'])
@login_required
def delete_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)

    # Ensure the current user owns this challenge
    if challenge.user_id != current_user.id:
        abort(403)

    db.session.delete(challenge)
    db.session.commit()
    flash('Challenge deleted successfully!', 'success')
    return redirect(url_for('challenges.list_challenges'))