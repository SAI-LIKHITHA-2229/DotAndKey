"""Production server: `python serve.py` (Waitress; works on Windows and Linux).

Unlike `python app.py` (Flask's development server) this is safe to run in
production. Put it behind an HTTPS reverse proxy and set APP_ENV=production,
SECRET_KEY and TRUST_PROXY (see .env.example).
"""
import logging
import os

from waitress import serve

from wsgi import app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve(app, host=os.environ.get("HOST", "0.0.0.0"),
          port=int(os.environ.get("PORT", 5001)), threads=8)
