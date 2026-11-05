"""WSGI entry point for production servers, e.g. `gunicorn wsgi:app` (Linux)."""
from api import create_app

app = create_app()
