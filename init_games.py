#!/usr/bin/env python
"""
Script to initialize game data in the database
"""
from app import create_app, db
from app.models.game import Game


def create_games():
    """Create initial game data"""
    games = [
        {
            'title': 'Memory Match',
            'description': 'Test your memory by finding matching pairs of cards.',
            'game_type': 'memory',
            'difficulty': 'Easy',
            'instructions': '''
                <ul>
                    <li>Click on cards to flip them over</li>
                    <li>Find all matching pairs of cards</li>
                    <li>Try to complete with as few moves as possible</li>
                    <li>The game ends when all pairs are matched</li>
                </ul>
            ''',
            'thumbnail': '/static/images/games/memory_match.jpg',
        },
        {
            'title': 'Snake',
            'description': 'Control a snake to eat food and grow longer without hitting walls or yourself.',
            'game_type': 'arcade',
            'difficulty': 'Medium',
            'instructions': '''
                <ul>
                    <li>Use arrow keys to control the snake</li>
                    <li>Eat food (red dots) to grow longer</li>
                    <li>Avoid hitting the walls or your own body</li>
                    <li>The game ends when you collide with a wall or yourself</li>
                </ul>
            ''',
            'thumbnail': '/static/images/games/snake.jpg',
        },
        {
            'title': 'Color Match',
            'description': 'Test your reflexes by matching colors as quickly as possible.',
            'game_type': 'puzzle',
            'difficulty': 'Easy',
            'instructions': '''
                <ul>
                    <li>Match the color of the text with the correct button</li>
                    <li>Be careful - the text color and the word might not match!</li>
                    <li>Try to get as many correct matches as possible in 60 seconds</li>
                </ul>
            ''',
            'thumbnail': '/static/images/games/color_match.jpg',
        },
        {
            'title': 'Math Challenge',
            'description': 'Solve math problems quickly to earn points. Test your arithmetic skills under pressure!',
            'game_type': 'puzzle',
            'difficulty': 'Medium',
            'instructions': '''
                <ul>
                    <li>Solve the arithmetic problem shown</li>
                    <li>Type in your answer and press Enter</li>
                    <li>Each correct answer earns 10 points</li>
                    <li>You have 60 seconds to solve as many problems as possible</li>
                </ul>
            ''',
            'thumbnail': '/static/images/games/math_challenge.jpg',
        },
    ]

    # Check if games already exist
    existing_count = Game.query.count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} games. Skipping initialization.")
        return

    # Create games
    for game_data in games:
        game = Game(
            title=game_data['title'],
            description=game_data['description'],
            game_type=game_data['game_type'],
            difficulty=game_data['difficulty'],
            instructions=game_data['instructions'],
            thumbnail=game_data['thumbnail'],
            active=True
        )
        db.session.add(game)

    db.session.commit()
    print(f"Successfully added {len(games)} games to the database.")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_games()