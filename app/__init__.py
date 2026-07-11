"""
Application Factory
Creates and configures Flask app
"""

import os
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from flasgger import Swagger

from .config import get_config
from .models import db
from .api.routes import api

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [{"endpoint": "apispec", "route": "/apispec.json", "rule_filter": lambda rule: True, "model_filter": lambda tag: True}],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs",
}

SWAGGER_TEMPLATE = {
    "info": {"title": "VT CourseHelper API", "description": "Professor ratings and course discussion aggregator for Virginia Tech", "version": "1.0.0"},
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
}


def create_app(env: str = None) -> Flask:
    frontend_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')

    app = Flask(__name__, static_folder=frontend_folder, static_url_path='')

    config = get_config(env)
    app.config.from_object(config)

    _setup_logging(app)

    db.init_app(app)
    CORS(app, origins='*', supports_credentials=False)
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    app.register_blueprint(api)

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    with app.app_context():
        db.create_all()
        app.logger.info("Database initialized")

    _setup_error_handlers(app)
    app.logger.info(f"App created: {env or 'default'}")
    return app


def _setup_logging(app: Flask) -> None:
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))


def _setup_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {str(error)}")
        return {'error': 'Internal server error'}, 500