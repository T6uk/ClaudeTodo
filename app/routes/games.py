# app/routes/games.py
"""
Enhanced Game routes for browsing, playing, and managing games
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import func
import os

from app import db
from app.models.game import Game
from app.models.game_score import GameScore

games_bp = Blueprint("games", __name__)

@games_bp.route("/games")
@login_required
def games():
    """Games listing page with advanced filtering and categorization"""
    # Get all active games
    all_games = Game.query.filter_by(active=True).all()

    # Group games by multiple attributes
    games_by_type = {}
    games_by_difficulty = {}

    for game in all_games:
        # Group by game type
        if game.game_type not in games_by_type:
            games_by_type[game.game_type] = []
        games_by_type[game.game_type].append(game)

        # Group by difficulty
        if game.difficulty not in games_by_difficulty:
            games_by_difficulty[game.difficulty] = []
        games_by_difficulty[game.difficulty].append(game)

    # Additional game statistics
    stats = {
        'total_games': len(all_games),
        'total_game_types': len(games_by_type),
        'game_type_counts': {k: len(v) for k, v in games_by_type.items()},
        'difficulty_counts': {k: len(v) for k, v in games_by_difficulty.items()}
    }

    return render_template("games/games.html",
                           title="Games",
                           all_games=all_games,
                           games_by_type=games_by_type,
                           games_by_difficulty=games_by_difficulty,
                           stats=stats)


@games_bp.route("/leaderboard")
@login_required
def leaderboard():
    """Leaderboard page for all games"""
    # Get all active games
    games = Game.query.filter_by(active=True).all()

    # Prepare leaderboards for each game
    leaderboards = {}
    for game in games:
        # Get top 10 scores for each game, ordered by score descending
        top_scores = GameScore.query.filter_by(game_id=game.id) \
            .order_by(GameScore.score.desc()) \
            .limit(10) \
            .all()

        leaderboards[game.id] = top_scores

    return render_template("games/leaderboard.html",
                           title="Game Leaderboards",
                           games=games,
                           leaderboards=leaderboards)


@games_bp.route("/play/<int:game_id>")
@login_required
def play_game(game_id):
    """Play a specific game"""
    game = Game.query.get_or_404(game_id)

    # Construct template path
    template_path = f"games/play/{game.game_type}/{game.title.lower().replace(' ', '_')}.html"

    # Check if template exists
    template_exists = False
    try:
        template_exists = os.path.exists(os.path.join('app', 'templates', template_path))
    except Exception as e:
        flash(f"Error checking template: {str(e)}", "danger")
        return redirect(url_for("games.games"))

    if not template_exists:
        flash(f"Game template not found for {game.title}", "danger")
        return redirect(url_for("games.games"))

    try:
        return render_template(template_path,
                               title=f"Play {game.title}",
                               game=game)
    except Exception as e:
        flash(f"Error rendering game template: {str(e)}", "danger")
        return redirect(url_for("games.games"))


@games_bp.route("/score", methods=["POST"])
@login_required
def record_score():
    """Record a game score"""
    game_id = request.form.get('game_id')
    score = request.form.get('score', type=int)

    if not game_id or score is None:
        flash("Invalid score submission", "danger")
        return redirect(url_for("games.games"))

    # Validate game exists
    game = Game.query.get_or_404(game_id)

    # Create new game score
    game_score = GameScore(
        user_id=current_user.id,
        game_id=game.id,
        score=score
    )

    db.session.add(game_score)
    db.session.commit()

    flash("Score recorded successfully!", "success")
    return redirect(url_for("games.leaderboard"))


@games_bp.route("/weekly-reset")
@login_required
def weekly_game_reset():
    """Reset weekly game leaderboards"""
    if not current_user.is_admin:
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for("games.leaderboard"))

    # Find games with weekly reset enabled
    weekly_reset_games = Game.query.filter_by(weekly_reset=True).all()
    reset_count = 0

    for game in weekly_reset_games:
        # Delete scores older than 7 days
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        GameScore.query.filter(
            GameScore.game_id == game.id,
            GameScore.date < one_week_ago
        ).delete(synchronize_session=False)
        reset_count += 1

    db.session.commit()
    flash(f"Weekly leaderboard reset completed for {reset_count} games.", "success")
    return redirect(url_for("games.leaderboard"))
