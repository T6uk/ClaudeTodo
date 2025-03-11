# app/routes/games.py
"""
Enhanced Game routes for browsing, playing, and managing games
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import func

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


@games_bp.route("/games/weekly-reset")
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