"""
Script to seed initial games in the database
"""
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.game import Game


def seed_games():
    """Seed the database with initial games"""
    games_data = [
        {
            'title': 'Color Match',
            'game_type': 'puzzle',
            'description': 'Test your speed and color recognition skills!',
            'difficulty': 'Easy',
            'thumbnail': '/static/images/games/color_match.jpg',
            'instructions': 'Match the color of the word, not the text itself.',
        },
        {
            'title': 'Math Challenge',
            'game_type': 'puzzle',
            'description': 'Solve math problems before time runs out!',
            'difficulty': 'Medium',
            'thumbnail': '/static/images/games/math_challenge.jpg',
            'instructions': 'Answer math problems as quickly as possible.',
        },
        {
            'title': 'Memory Match',
            'game_type': 'puzzle',
            'description': 'Test your memory by matching card pairs!',
            'difficulty': 'Easy',
            'thumbnail': '/static/images/games/memory_match.jpg',
            'instructions': 'Flip cards and match identical pairs.',
        },
        {
            'title': 'Snake',
            'game_type': 'arcade',
            'description': 'Classic snake game - eat food and grow!',
            'difficulty': 'Medium',
            'thumbnail': '/static/images/games/snake.jpg',
            'instructions': 'Use arrow keys to control the snake. Avoid walls and yourself.',
        }
    ]

    # Track changes
    added_games = 0
    existing_games = 0

    for game_info in games_data:
        existing_game = Game.query.filter_by(title=game_info['title']).first()
        if not existing_game:
            game = Game(**game_info)
            db.session.add(game)
            added_games += 1
        else:
            existing_games += 1

    db.session.commit()

    print(f"Game seeding complete:")
    print(f"- Added {added_games} new games")
    print(f"- {existing_games} games already existed")


def main():
    app = create_app()
    with app.app_context():
        seed_games()


if __name__ == "__main__":
    main()