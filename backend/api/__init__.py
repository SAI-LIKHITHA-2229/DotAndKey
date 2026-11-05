"""Dot & Key store API: application factory."""
import logging

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from . import addresses, auth, cart, catalog, orders
from .config import load_config
from .db import init_db
from .extensions import limiter

log = logging.getLogger(__name__)


def create_app(overrides=None):
    """Create the Flask app. `overrides` replaces config values (used by tests)."""
    app = Flask(__name__)
    app.config.update(load_config(overrides))

    # Only needed when the frontend is served from a different origin than
    # the API; credentials let the session cookie through for those origins.
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)
    limiter.init_app(app)

    for module in (auth, catalog, cart, addresses, orders):
        app.register_blueprint(module.bp)

    register_error_handlers(app)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    # Create tables on startup, however the app is launched.
    with app.app_context():
        init_db()

    return app


def register_error_handlers(app):
    # Always answer with JSON, never an HTML error page.
    @app.errorhandler(429)
    def handle_rate_limited(_error):
        return jsonify({"error": "Too many attempts. Please wait a minute and try again."}), 429

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(_error):
        log.exception("Unhandled error")
        return jsonify({"error": "Something went wrong on our side"}), 500
