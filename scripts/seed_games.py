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
            'instructions': 'Match the color of the word, not the text itself. Click the button that corresponds to the color that the word is displayed in, not what the word says.',
        },
        {
            'title': 'Math Challenge',
            'game_type': 'puzzle',
            'description': 'Solve math problems before time runs out!',
            'difficulty': 'Medium',
            'thumbnail': '/static/images/games/math_challenge.jpg',
            'instructions': 'Answer math problems as quickly as possible. Type your answer and press Enter to submit.',
        },
        {
            'title': 'Memory Match',
            'game_type': 'puzzle',
            'description': 'Test your memory by matching card pairs!',
            'difficulty': 'Easy',
            'thumbnail': '/static/images/games/memory_match.jpg',
            'instructions': 'Flip cards and match identical pairs. Remember the positions of cards you\'ve seen to find matches more efficiently.',
        },
        {
            'title': 'Snake',
            'game_type': 'arcade',
            'description': 'Classic snake game - eat food and grow!',
            'difficulty': 'Medium',
            'thumbnail': '/static/images/games/snake.jpg',
            'instructions': 'Use arrow keys to control the snake. Eat the food to grow longer. Avoid colliding with walls and yourself.',
            'weekly_reset': True,
        },
        {
            'title': 'Word Scramble',
            'game_type': 'word',
            'description': 'Unscramble words before time runs out!',
            'difficulty': 'Medium',
            'thumbnail': '/static/images/games/word_scramble.jpg',
            'instructions': 'Unscramble words from jumbled letters. Type your answer and press Enter to submit. Use the hint if you get stuck!',
            'weekly_reset': True,
        }
    ]

    # Track changes
    added_games = 0
    updated_games = 0
    existing_games = 0

    for game_info in games_data:
        existing_game = Game.query.filter_by(title=game_info['title']).first()
        if not existing_game:
            game = Game(**game_info)
            db.session.add(game)
            added_games += 1
        else:
            # Update existing game with new information
            for key, value in game_info.items():
                setattr(existing_game, key, value)
            updated_games += 1
            existing_games += 1

    db.session.commit()

    print(f"Game seeding complete:")
    print(f"- Added {added_games} new games")
    print(f"- Updated {updated_games} existing games")
    print(f"- {existing_games - updated_games} games unchanged")


def main():
    app = create_app()
    with app.app_context():
        seed_games()


if __name__ == "__main__":
    main()