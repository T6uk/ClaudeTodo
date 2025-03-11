# app/routes/games.py
"""
Game routes for browsing and playing games
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from datetime import datetime

from app import db
from app.models.game import Game
from app.models.game_score import GameScore

games_bp = Blueprint("games", __name__)


@games_bp.route("/games")
@login_required
def games():
    """Games listing page"""
    # Get all active games
    all_games = Game.query.filter_by(active=True).all()

    # Group games by type
    games_by_type = {}
    for game in all_games:
        if game.game_type not in games_by_type:
            games_by_type[game.game_type] = []
        games_by_type[game.game_type].append(game)

    return render_template("games/games.html",
                           title="Games",
                           all_games=all_games,
                           games_by_type=games_by_type)


@games_bp.route("/games/<int:game_id>")
@login_required
def play_game(game_id):
    """Play a specific game"""
    game = Game.query.get_or_404(game_id)

    # Get user's high score for this game
    high_score = GameScore.query.filter_by(
        user_id=current_user.id,
        game_id=game_id
    ).order_by(GameScore.score.desc()).first()

    # Get top scores for the game
    top_scores = GameScore.query.filter_by(
        game_id=game_id
    ).order_by(GameScore.score.desc()).limit(10).all()

    return render_template(f"games/play/{game.game_type}/{game.title.lower().replace(' ', '_')}.html",
                           title=game.title,
                           game=game,
                           high_score=high_score,
                           top_scores=top_scores)


@games_bp.route("/games/<int:game_id>/save-score", methods=["POST"])
@login_required
def save_score(game_id):
    """Save a game score"""
    game = Game.query.get_or_404(game_id)

    # Get score from request
    score = request.form.get('score', type=int)
    if score is None:
        data = request.get_json()
        if data:
            score = data.get('score')

    if not score:
        flash("No score provided", "danger")
        return redirect(url_for("games.play_game", game_id=game_id))

    # Save the score
    game_score = GameScore(
        user_id=current_user.id,
        game_id=game_id,
        score=score
    )

    db.session.add(game_score)
    db.session.commit()

    flash(f"Score of {score} saved successfully!", "success")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "score": score})

    return redirect(url_for("games.play_game", game_id=game_id))


@games_bp.route("/games/leaderboard")
@login_required
def leaderboard():
    """Global game leaderboard"""
    games = Game.query.filter_by(active=True).all()

    # Get top score for each game
    leaderboards = {}
    for game in games:
        top_scores = GameScore.query.filter_by(
            game_id=game.id
        ).order_by(GameScore.score.desc()).limit(10).all()

        leaderboards[game.id] = top_scores

    return render_template("games/leaderboard.html",
                           title="Games Leaderboard",
                           games=games,
                           leaderboards=leaderboards)