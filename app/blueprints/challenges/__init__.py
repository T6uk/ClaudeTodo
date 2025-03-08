from flask import Blueprint

challenges_bp = Blueprint('challenges', __name__, url_prefix='/challenges')

from app.blueprints.challenges import routes