import datetime
import re
import sqlite3
from contextlib import closing
from functools import wraps

import jwt
from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db_connection
from .extensions import limiter
from .validation import json_body, raw_text_field, text_field

bp = Blueprint("auth", __name__)

# ---- Account rules ----
USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_.]{3,30}")
PASSWORD_MIN, PASSWORD_MAX = 8, 128

# Checked when a username doesn't exist, so a failed login takes the same
# time either way and can't reveal which usernames are registered.
DUMMY_PASSWORD_HASH = generate_password_hash("not-a-real-password")

# ---- Sessions ----
# Browsers keep the JWT in an httpOnly cookie that page JavaScript cannot
# read, so a script injected into the page cannot steal it. API clients
# (curl, Postman, mobile apps) may send it as "Authorization: Bearer <jwt>".
SESSION_COOKIE = "dk_session"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
CSRF_HEADER = "X-Requested-With"


def _issue_token(user):
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        hours=current_app.config["TOKEN_HOURS"]
    )
    token = jwt.encode(
        {"user_id": user["id"], "username": user["username"],
         "ver": user["token_version"], "exp": expires},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return token, expires


def _authenticate():
    """Return (user_row, token_payload, from_cookie) or (None, error_message, None)."""
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        token, from_cookie = header[len("Bearer "):], False
    else:
        token, from_cookie = request.cookies.get(SESSION_COOKIE), True
    if not token:
        return None, "Login required", None

    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None, "Your session has expired. Please sign in again.", None

    with closing(get_db_connection()) as conn:
        user = conn.execute(
            "SELECT id, username, token_version FROM users WHERE id = ?",
            (payload.get("user_id"),)
        ).fetchone()

    # The user must still exist and must not have logged out since the
    # token was issued (logout bumps token_version).
    if user is None or user["token_version"] != payload.get("ver"):
        return None, "Your session has ended. Please sign in again.", None
    return user, payload, from_cookie


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user, payload, from_cookie = _authenticate()
        if user is None:
            return jsonify({"error": payload}), 401

        # Cookies are sent automatically, so a write authenticated by cookie
        # must also carry a custom header. Other sites cannot add one without
        # passing CORS, which blocks cross-site request forgery.
        if from_cookie and request.method not in SAFE_METHODS \
                and request.headers.get(CSRF_HEADER) != "XMLHttpRequest":
            return jsonify({"error": f"Missing {CSRF_HEADER} header"}), 403

        g.user_id = user["id"]
        g.username = user["username"]
        g.token_expires = datetime.datetime.fromtimestamp(payload["exp"], datetime.timezone.utc)
        return view(*args, **kwargs)

    return wrapped


@bp.route("/register", methods=["POST"])
@limiter.limit("10 per hour")          # slows down mass account creation
def register():
    data = json_body()
    username = text_field(data, "username")
    password = raw_text_field(data, "password")

    if not USERNAME_PATTERN.fullmatch(username):
        return jsonify({"error": "Username must be 3-30 characters: letters, "
                                 "numbers, dots or underscores"}), 400
    if not PASSWORD_MIN <= len(password) <= PASSWORD_MAX:
        return jsonify({"error": f"Password must be {PASSWORD_MIN}-{PASSWORD_MAX} "
                                 "characters"}), 400

    password_hash = generate_password_hash(password)

    try:
        with closing(get_db_connection()) as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already taken"}), 409

    return jsonify({"message": "Account created"}), 201


@bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute; 50 per hour")   # stops password guessing
def login():
    data = json_body()
    username = text_field(data, "username")
    password = raw_text_field(data, "password")

    with closing(get_db_connection()) as conn:
        user = conn.execute(
            "SELECT id, username, password_hash, token_version FROM users "
            "WHERE lower(username) = lower(?)",
            (username,)
        ).fetchone()

    stored_hash = user["password_hash"] if user else DUMMY_PASSWORD_HASH
    password_ok = check_password_hash(stored_hash, password)
    if user is None or not password_ok:
        return jsonify({"error": "Invalid username or password"}), 401

    token, expires = _issue_token(user)
    response = jsonify({"username": user["username"], "expires_at": expires.isoformat()})
    response.set_cookie(
        SESSION_COOKIE, token,
        max_age=current_app.config["TOKEN_HOURS"] * 3600,
        httponly=True,                                    # unreadable by page JavaScript
        secure=current_app.config["SESSION_COOKIE_SECURE"],
        samesite="Lax",                                   # not sent on cross-site POSTs
        path="/",
    )
    return response, 200


@bp.route("/me")
@login_required
def me():
    return jsonify({"username": g.username, "expires_at": g.token_expires.isoformat()})


@bp.route("/logout", methods=["POST"])
def logout():
    # Ending the session server-side: bumping token_version invalidates this
    # token and any copies of it, on every device.
    user, _, _ = _authenticate()
    if user is not None:
        with closing(get_db_connection()) as conn:
            conn.execute(
                "UPDATE users SET token_version = token_version + 1 WHERE id = ?", (user["id"],)
            )
            conn.commit()

    response = jsonify({"message": "Logged out"})
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response, 200
