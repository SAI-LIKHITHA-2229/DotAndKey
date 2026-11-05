import logging
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
DEV_SECRET_KEY = "dev-only-insecure-key-change-me-in-production"

log = logging.getLogger(__name__)


def load_config():
    """Build the app configuration from environment variables."""
    app_env = os.environ.get("APP_ENV", "development")

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        if app_env == "production":
            raise RuntimeError("SECRET_KEY must be set in production")
        log.warning("SECRET_KEY not set; using an insecure development key")
        secret_key = DEV_SECRET_KEY

    cors_origins = [
        origin.strip()
        for origin in os.environ.get(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]

    return {
        "APP_ENV": app_env,
        "SECRET_KEY": secret_key,
        "DATABASE_PATH": os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "cart.db")),
        "CORS_ORIGINS": cors_origins,
        "TOKEN_HOURS": 12,
        "MAX_CONTENT_LENGTH": 32 * 1024,   # requests are small JSON bodies
    }
