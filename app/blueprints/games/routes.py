from flask import render_template, redirect, url_for
from flask_login import login_required
from app.blueprints.games import games_bp


@games_bp.route('/')
@login_required
def list_games():
    games = [
        {
            'id': 'memory',
            'name': 'Memory Match',
            'description': 'Test your memory by matching pairs of cards.',
            'icon': 'bi-grid-3x3-gap'
        },
        {
            'id': 'hangman',
            'name': 'Hangman',
            'description': 'Guess the word before you run out of attempts.',
            'icon': 'bi-pencil'
        },
        {
            'id': 'tictactoe',
            'name': 'Tic Tac Toe',
            'description': 'Classic game of X and O.',
            'icon': 'bi-grid-3x3'
        },
        {
            'id': 'snake',
            'name': 'Snake',
            'description': 'Control the snake to eat food and grow without hitting the walls or yourself.',
            'icon': 'bi-arrow-right'
        }
    ]
    return render_template('games/list.html', title='Games', games=games)


@games_bp.route('/memory')
@login_required
def memory_game():
    return render_template('games/memory.html', title='Memory Match Game')


@games_bp.route('/hangman')
@login_required
def hangman_game():
    return render_template('games/hangman.html', title='Hangman Game')


@games_bp.route('/tictactoe')
@login_required
def tictactoe_game():
    return render_template('games/tictactoe.html', title='Tic Tac Toe Game')


@games_bp.route('/snake')
@login_required
def snake_game():
    return render_template('games/snake.html', title='Snake Game')
