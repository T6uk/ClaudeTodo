"""
Challenge routes for user challenges
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.challenge import Challenge
from app.forms.challenge_forms import ChallengeForm

challenge_bp = Blueprint("challenge", __name__)


@challenge_bp.route("/challenges")
@login_required
def challenges():
    """Challenge list page"""
    active_challenges = Challenge.query.filter_by(status='active').all()
    completed_challenges = Challenge.query.filter_by(status='completed').all()
    deleted_challenges = Challenge.query.filter_by(status='deleted').all()

    form = ChallengeForm()

    # Set default start date to now
    form.start_date.data = datetime.utcnow()

    # Set up user choices for participants field
    users = User.query.all()
    form.participants.choices = [(u.id, u.username) for u in users]

    # Get statistics
    stats = {
        'total_active': len(active_challenges),
        'total_completed': len(completed_challenges),
        'total_created': Challenge.query.filter_by(creator_id=current_user.id).count(),
        'total_joined': Challenge.query.join(Challenge.participants).filter(User.id == current_user.id).count(),
        'categories': db.session.query(
            Challenge.category,
            func.count(Challenge.id)
        ).group_by(Challenge.category).all()
    }

    return render_template("challenge/challenges.html",
                           title="Challenges",
                           active_challenges=active_challenges,
                           completed_challenges=completed_challenges,
                           deleted_challenges=deleted_challenges,
                           stats=stats,
                           form=form)


@challenge_bp.route("/challenges/create", methods=["POST"])
@login_required
def create_challenge():
    """Create a new challenge"""
    form = ChallengeForm()

    # Set up user choices for participants field
    users = User.query.all()
    form.participants.choices = [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        # Create new challenge
        challenge = Challenge(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            target_value=form.target_value.data,
            measurement_unit=form.measurement_unit.data,
            creator_id=current_user.id
        )

        # Add participants
        if form.participants.data:
            participant_users = User.query.filter(User.id.in_(form.participants.data)).all()
            challenge.participants = participant_users

            # Add creator as a participant if not already included
            if current_user not in challenge.participants:
                challenge.participants.append(current_user)
        else:
            # If no participants selected, at least add the creator
            challenge.participants.append(current_user)

        # Add to database
        db.session.add(challenge)
        db.session.commit()

        flash("Challenge created successfully!", "success")
        return redirect(url_for("challenge.challenges"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("challenge.challenges"))


@challenge_bp.route("/challenges/<int:challenge_id>")
@login_required
def get_challenge(challenge_id):
    """Get challenge details for modal"""
    challenge = Challenge.query.get_or_404(challenge_id)
    return jsonify(challenge.to_dict())


@challenge_bp.route("/challenges/<int:challenge_id>/update", methods=["POST"])
@login_required
def update_challenge(challenge_id):
    """Update an existing challenge"""
    challenge = Challenge.query.get_or_404(challenge_id)
    form = ChallengeForm()

    # Set up user choices for participants field
    users = User.query.all()
    form.participants.choices = [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        # Update challenge fields
        challenge.title = form.title.data
        challenge.description = form.description.data
        challenge.category = form.category.data
        challenge.start_date = form.start_date.data
        challenge.end_date = form.end_date.data
        challenge.status = form.status.data
        challenge.target_value = form.target_value.data
        challenge.measurement_unit = form.measurement_unit.data

        # Update participants
        if form.participants.data:
            participant_users = User.query.filter(User.id.in_(form.participants.data)).all()
            challenge.participants = participant_users

            # Add creator as a participant if not already included
            if current_user not in challenge.participants:
                challenge.participants.append(current_user)
        else:
            # If no participants selected, at least add the creator
            challenge.participants = [current_user]

        db.session.commit()
        flash("Challenge updated successfully!", "success")
        return redirect(url_for("challenge.challenges"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "danger")

    return redirect(url_for("challenge.challenges"))


@challenge_bp.route("/challenges/<int:challenge_id>/delete", methods=["POST"])
@login_required
def delete_challenge(challenge_id):
    """Mark a challenge as deleted"""
    challenge = Challenge.query.get_or_404(challenge_id)

    # Only allow creator to delete
    if challenge.creator_id != current_user.id:
        flash("You don't have permission to delete this challenge.", "danger")
        return redirect(url_for("challenge.challenges"))

    challenge.status = 'deleted'
    db.session.commit()

    flash("Challenge deleted successfully!", "success")
    return redirect(url_for("challenge.challenges"))


@challenge_bp.route("/challenges/<int:challenge_id>/complete", methods=["POST"])
@login_required
def complete_challenge(challenge_id):
    """Mark a challenge as completed"""
    challenge = Challenge.query.get_or_404(challenge_id)

    # Only allow creator to complete
    if challenge.creator_id != current_user.id:
        flash("You don't have permission to complete this challenge.", "danger")
        return redirect(url_for("challenge.challenges"))

    challenge.status = 'completed'

    # If target_value is set, update current_value to target_value
    if challenge.target_value:
        challenge.current_value = challenge.target_value

    db.session.commit()

    flash("Challenge marked as completed!", "success")
    return redirect(url_for("challenge.challenges"))


@challenge_bp.route("/challenges/<int:challenge_id>/reactivate", methods=["POST"])
@login_required
def reactivate_challenge(challenge_id):
    """Reactivate a deleted or completed challenge"""
    challenge = Challenge.query.get_or_404(challenge_id)

    # Only allow creator to reactivate
    if challenge.creator_id != current_user.id:
        flash("You don't have permission to reactivate this challenge.", "danger")
        return redirect(url_for("challenge.challenges"))

    challenge.status = 'active'
    db.session.commit()

    flash("Challenge reactivated successfully!", "success")
    return redirect(url_for("challenge.challenges"))


@challenge_bp.route("/challenges/<int:challenge_id>/leave", methods=["POST"])
@login_required
def leave_challenge(challenge_id):
    """Leave a challenge"""
    challenge = Challenge.query.get_or_404(challenge_id)

    # Can't leave if you're the creator
    if challenge.creator_id == current_user.id:
        flash("As the creator, you cannot leave this challenge.", "warning")
        return redirect(url_for("challenge.challenges"))

    if current_user in challenge.participants:
        challenge.participants.remove(current_user)
        db.session.commit()
        flash("You have left the challenge.", "success")
    else:
        flash("You are not a participant in this challenge.", "warning")

    return redirect(url_for("challenge.challenges"))


@challenge_bp.route("/challenges/<int:challenge_id>/join", methods=["POST"])
@login_required
def join_challenge(challenge_id):
    """Join a challenge"""
    challenge = Challenge.query.get_or_404(challenge_id)

    # Only allow joining active challenges
    if challenge.status != 'active':
        flash("You can only join active challenges.", "warning")
        return redirect(url_for("challenge.challenges"))

    if current_user not in challenge.participants:
        challenge.participants.append(current_user)
        db.session.commit()
        flash("You have joined the challenge!", "success")
    else:
        flash("You are already a participant in this challenge.", "info")

    return redirect(url_for("challenge.challenges"))


@challenge_bp.route("/challenges/<int:challenge_id>/update-progress", methods=["POST"])
@login_required
def update_progress(challenge_id):
    """Update challenge progress"""
    challenge = Challenge.query.get_or_404(challenge_id)

    # Check if user is a participant
    if current_user not in challenge.participants and current_user.id != challenge.creator_id:
        flash("You must be a participant to update progress.", "danger")
        return redirect(url_for("challenge.challenges"))

    # Get progress value from form
    progress_value = request.form.get('progress_value', type=float)

    if progress_value is not None:
        if challenge.target_value and progress_value > challenge.target_value:
            # Cap progress at target value
            challenge.current_value = challenge.target_value
        else:
            challenge.current_value = progress_value

        # If we've reached 100%, ask if they want to complete the challenge
        if challenge.target_value and challenge.current_value >= challenge.target_value:
            challenge.current_value = challenge.target_value
            db.session.commit()
            flash("You've reached the target! You can now mark the challenge as completed.", "success")
        else:
            db.session.commit()
            flash("Progress updated successfully!", "success")
    else:
        flash("Invalid progress value.", "danger")

    return redirect(url_for("challenge.challenges"))