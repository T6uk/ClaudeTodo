# app/routes/games.py
"""
Enhanced Game routes for browsing, playing, and managing games
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from sqlalchemy.sql import text
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
    """Enhanced leaderboard page with filtering and personal bests"""
    # Get filter parameters
    game_id = request.args.get('game_id', type=int)
    period = request.args.get('period', 'all')  # 'all' or 'weekly'

    # Get all active games
    all_games = Game.query.filter_by(active=True).all()

    # Filter games by game_id if provided
    displayed_games = [game for game in all_games if game_id is None or game.id == game_id]

    # Create a map of game_id to game for easy lookup
    game_map = {game.id: game for game in all_games}

    # Time filter - for weekly scores
    time_filter = None
    if period == 'weekly':
        time_filter = datetime.utcnow() - timedelta(days=7)

    # Prepare leaderboards for each game
    leaderboards = {}
    for game in displayed_games:
        # Prepare query
        query = GameScore.query.filter_by(game_id=game.id)

        # Apply time filter if specified
        if time_filter:
            query = query.filter(GameScore.date >= time_filter)

        # Get top 10 scores for each game, ordered by score descending
        top_scores = query.order_by(GameScore.score.desc()).limit(10).all()

        leaderboards[game.id] = top_scores

    # Get personal bests for each game
    personal_bests = {}
    for game in all_games:
        # Get the user's best score for this game
        best_score = GameScore.query.filter_by(
            game_id=game.id,
            user_id=current_user.id
        ).order_by(GameScore.score.desc()).first()

        if best_score:
            # Count total players for this game
            total_players = db.session.query(func.count(func.distinct(GameScore.user_id))).filter_by(
                game_id=game.id).scalar()

            # Find the user's rank
            rank_query = text("""
                SELECT player_rank FROM (
                    SELECT user_id, RANK() OVER (ORDER BY MAX(score) DESC) as player_rank
                    FROM game_scores
                    WHERE game_id = :game_id
                    GROUP BY user_id
                ) as rankings
                WHERE user_id = :user_id
            """)

            try:
                result = db.engine.execute(rank_query, game_id=game.id, user_id=current_user.id).first()
                rank = result[0] if result else None
            except Exception:
                # Fallback to a simpler approach if the SQL query fails
                rank = None
                scores_above = GameScore.query.with_entities(
                    func.max(GameScore.score)
                ).filter(
                    GameScore.game_id == game.id
                ).group_by(
                    GameScore.user_id
                ).having(
                    func.max(GameScore.score) > best_score.score
                ).count()

                if rank is None:
                    rank = scores_above + 1

            # Get the top score for this game
            top_score = GameScore.query.filter_by(game_id=game.id).order_by(GameScore.score.desc()).first()
            top_score_value = top_score.score if top_score else None

            # Count how many times the user has played this game
            games_played = GameScore.query.filter_by(
                game_id=game.id,
                user_id=current_user.id
            ).count()

            personal_bests[game.id] = {
                'score': best_score.score,
                'date': best_score.date,
                'rank': rank,
                'total_players': total_players,
                'top_score': top_score_value,
                'games_played': games_played
            }

    # Compile user statistics
    user_stats = {
        'total_games_played': GameScore.query.filter_by(user_id=current_user.id).count(),
        'total_score': db.session.query(func.sum(GameScore.score)).filter_by(user_id=current_user.id).scalar() or 0,
        'personal_bests': len(personal_bests),
        'top_rank': min([pb['rank'] for pb in personal_bests.values()]) if personal_bests else 'N/A',
        'weekly_played': GameScore.query.filter(
            GameScore.user_id == current_user.id,
            GameScore.date >= datetime.utcnow() - timedelta(days=7)
        ).count()
    }

    return render_template("games/leaderboard.html",
                           title="Game Leaderboards",
                           games=all_games,
                           displayed_games=displayed_games,
                           leaderboards=leaderboards,
                           personal_bests=personal_bests,
                           game_map=game_map,
                           period=period,
                           user_stats=user_stats)


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
        # Get user's personal best for this game
        personal_best = GameScore.query.filter_by(
            game_id=game.id,
            user_id=current_user.id
        ).order_by(GameScore.score.desc()).first()

        # Get global best score for this game
        global_best = GameScore.query.filter_by(
            game_id=game.id
        ).order_by(GameScore.score.desc()).first()

        return render_template(template_path,
                               title=f"Play {game.title}",
                               game=game,
                               personal_best=personal_best,
                               global_best=global_best)
    except Exception as e:
        flash(f"Error rendering game template: {str(e)}", "danger")
        return redirect(url_for("games.games"))


@games_bp.route("/score", methods=["POST"])
@login_required
def record_score():
    """Record a game score"""
    game_id = request.form.get('game_id', type=int)
    score = request.form.get('score', type=int)

    if not game_id or score is None:
        flash("Invalid score submission", "danger")
        return redirect(url_for("games.games"))

    # Validate game exists
    game = Game.query.get_or_404(game_id)

    # Check for cheating (extremely high scores)
    highest_score = GameScore.query.filter_by(game_id=game_id).order_by(GameScore.score.desc()).first()

    if highest_score and score > highest_score.score * 2 and highest_score.score > 1000:
        # This might be cheating if it's more than double the highest score
        flash("Suspicious score detected. Please try again.", "warning")
        return redirect(url_for("games.play_game", game_id=game_id))

    # Create new game score
    game_score = GameScore(
        user_id=current_user.id,
        game_id=game.id,
        score=score
    )

    db.session.add(game_score)
    db.session.commit()

    # Check if this is a new personal best
    personal_best = GameScore.query.filter(
        GameScore.game_id == game.id,
        GameScore.user_id == current_user.id,
        GameScore.id != game_score.id  # Exclude the score we just added
    ).order_by(GameScore.score.desc()).first()

    if not personal_best or score > personal_best.score:
        flash(f"New personal best: {score}!", "success")
    else:
        flash(f"Score recorded: {score}. Your best is {personal_best.score}.", "success")

    return redirect(url_for("games.leaderboard", game_id=game_id))


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