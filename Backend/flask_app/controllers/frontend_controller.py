import os
from flask import Blueprint, send_from_directory

frontend_bp = Blueprint('frontend', __name__, url_prefix='')

static_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'dist')

@frontend_bp.route('/', defaults={'path': ''})
@frontend_bp.route('/<path:path>')
def serve_react(path):
    if path != '' and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')