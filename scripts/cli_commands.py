"""
Flask CLI commands for running scheduled tasks
"""
import os
import sys
import click
from datetime import datetime, timedelta
from app import create_app, db
from app.models.game import Game
from app.models.game_score import GameScore

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

app = create_app()


@app.cli.group()
def games():
    """Commands for managing games."""
    pass


@games.command()
def reset_weekly_leaderboards():
    """Reset weekly leaderboards for eligible games."""
    with app.app_context():
        # Find games with weekly reset enabled
        weekly_reset_games = Game.query.filter_by(weekly_reset=True, active=True).all()

        if not weekly_reset_games:
            click.echo("No games found with weekly reset enabled.")
            return

        reset_count = 0
        score_count = 0

        for game in weekly_reset_games:
            # Calculate the date one week ago
            one_week_ago = datetime.utcnow() - timedelta(days=7)

            # Count scores to be deleted
            scores_to_delete = GameScore.query.filter(
                GameScore.game_id == game.id,
                GameScore.date < one_week_ago
            ).count()

            # Delete scores older than one week
            if scores_to_delete > 0:
                GameScore.query.filter(
                    GameScore.game_id == game.id,
                    GameScore.date < one_week_ago
                ).delete(synchronize_session=False)

                reset_count += 1
                score_count += scores_to_delete

        db.session.commit()

        click.echo(f"Weekly leaderboard reset completed:")
        click.echo(f"- Reset {reset_count} out of {len(weekly_reset_games)} eligible games")
        click.echo(f"- Removed {score_count} old scores")

        if reset_count == 0:
            click.echo("No scores needed to be reset.")


@games.command()
def list_games():
    """List all available games."""
    with app.app_context():
        games = Game.query.order_by(Game.game_type, Game.title).all()

        if not games:
            click.echo("No games found in the database.")
            return

        click.echo(f"Found {len(games)} games:")
        for game in games:
            status = "✅ Active" if game.active else "❌ Inactive"
            weekly = "🔄 Weekly Reset" if game.weekly_reset else "📊 All-time"
            click.echo(f"[{game.id}] {game.title} ({game.game_type}) - {status} - {weekly}")


@games.command()
@click.argument('game_id', type=int)
def game_stats(game_id):
    """Show statistics for a specific game."""
    with app.app_context():
        game = Game.query.get(game_id)

        if not game:
            click.echo(f"No game found with ID {game_id}")
            return

        click.echo(f"Statistics for game: {game.title}")
        click.echo(f"Type: {game.game_type}")
        click.echo(f"Difficulty: {game.difficulty}")
        click.echo(f"Active: {'Yes' if game.active else 'No'}")
        click.echo(f"Weekly Reset: {'Yes' if game.weekly_reset else 'No'}")

        # Calculate score statistics
        total_scores = GameScore.query.filter_by(game_id=game.id).count()
        total_players = db.session.query(db.func.count(db.func.distinct(GameScore.user_id))) \
            .filter(GameScore.game_id == game.id).scalar()

        highest_score = GameScore.query.filter_by(game_id=game.id) \
            .order_by(GameScore.score.desc()).first()

        average_score = db.session.query(db.func.avg(GameScore.score)) \
            .filter(GameScore.game_id == game.id).scalar()

        click.echo("\nScore Statistics:")
        click.echo(f"Total Plays: {total_scores}")
        click.echo(f"Unique Players: {total_players}")

        if highest_score:
            click.echo(f"Highest Score: {highest_score.score} (by User ID: {highest_score.user_id})")

        if average_score:
            click.echo(f"Average Score: {average_score:.2f}")


if __name__ == "__main__":
    app.cli.main()
