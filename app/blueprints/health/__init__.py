from flask import Blueprint

health_bp = Blueprint('health', __name__, url_prefix='/health')

from app.blueprints.health import routes