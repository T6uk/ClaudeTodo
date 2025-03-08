from flask import Blueprint

workout_bp = Blueprint('workout', __name__, url_prefix='/workout')

from app.blueprints.workout import routes