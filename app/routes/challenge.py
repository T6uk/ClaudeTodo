"""
Challenge routes for user challenges
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime

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

    return render_template("challenge/challenges.html",
                           title="Challenges",
                           active_challenges=active_challenges,
                           completed_challenges=completed_challenges,
                           deleted_challenges=deleted_challenges,
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
            start_date=form.start_date.data,
            end_date=form.end_date.data,
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
        challenge.start_date = form.start_date.data
        challenge.end_date = form.end_date.data
        challenge.status = form.status.data

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