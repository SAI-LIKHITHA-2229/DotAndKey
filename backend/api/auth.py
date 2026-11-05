import datetime
import re
import sqlite3
from contextlib import closing
from functools import wraps

import jwt
from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db_connection

bp = Blueprint("auth", __name__)

# ---- Account rules ----
USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_.]{3,30}")
PASSWORD_MIN, PASSWORD_MAX = 8, 128


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Login required"}), 401

        token = header[len("Bearer "):]
        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid or expired token"}), 401

        g.user_id = payload["user_id"]
        return view(*args, **kwargs)

    return wrapped


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

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
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    with closing(get_db_connection()) as conn:
        user = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        hours=current_app.config["TOKEN_HOURS"]
    )
    token = jwt.encode(
        {"user_id": user["id"], "username": user["username"], "exp": expires},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    return jsonify({"token": token, "username": user["username"]}), 200
