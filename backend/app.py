import datetime
import json
import os
import sqlite3
from contextlib import closing
from functools import wraps

import jwt
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DISCOUNT_PERCENT = 20


def get_db_connection():
    # timeout / busy_timeout: wait for a lock instead of failing or hanging.
    conn = sqlite3.connect("cart.db", timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db():
    with closing(get_db_connection()) as conn:
        # WAL lets readers and a writer work concurrently without blocking,
        # which keeps the dev server from wedging under rapid clicks.
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                image TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                items TEXT NOT NULL,
                total INTEGER NOT NULL,
                address TEXT,
                payment_method TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Migrate older databases created before these columns existed.
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(cart)")]
        if "image" not in columns:
            conn.execute("ALTER TABLE cart ADD COLUMN image TEXT")
        if "user_id" not in columns:
            conn.execute("ALTER TABLE cart ADD COLUMN user_id INTEGER")

        conn.commit()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Login required"}), 401

        token = header[len("Bearer "):]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid or expired token"}), 401

        g.user_id = payload["user_id"]
        return view(*args, **kwargs)

    return wrapped


@app.route("/cart")
@login_required
def get_cart():
    with closing(get_db_connection()) as conn:
        items = conn.execute(
            "SELECT * FROM cart WHERE user_id = ?", (g.user_id,)
        ).fetchall()
    return jsonify([dict(item) for item in items])


@app.route("/cart", methods=["POST"])
@login_required
def add_to_cart():
    new_item = request.get_json(silent=True) or {}
    if not new_item.get("product_name"):
        return jsonify({"error": "product_name is required"}), 400

    with closing(get_db_connection()) as conn:
        existing = conn.execute(
            "SELECT id FROM cart WHERE product_name = ? AND user_id = ?",
            (new_item["product_name"], g.user_id)
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE cart SET quantity = quantity + 1 WHERE id = ?",
                (existing["id"],)
            )
        else:
            conn.execute(
                "INSERT INTO cart (product_name, price, quantity, image, user_id) "
                "VALUES (?, ?, ?, ?, ?)",
                (new_item["product_name"], new_item.get("price", 0), 1,
                 new_item.get("image"), g.user_id)
            )
        conn.commit()

    return jsonify({"message": "Item added to cart"}), 201


@app.route("/cart/<int:item_id>", methods=["DELETE"])
@login_required
def remove_from_cart(item_id):
    with closing(get_db_connection()) as conn:
        conn.execute(
            "DELETE FROM cart WHERE id = ? AND user_id = ?", (item_id, g.user_id)
        )
        conn.commit()
    return jsonify({"message": "Item removed from cart"}), 200


@app.route("/cart/<int:item_id>/decrease", methods=["PUT"])
@login_required
def decrease_quantity(item_id):
    with closing(get_db_connection()) as conn:
        item = conn.execute(
            "SELECT quantity FROM cart WHERE id = ? AND user_id = ?",
            (item_id, g.user_id)
        ).fetchone()

        if item is None:
            return jsonify({"error": "Item not found"}), 404

        if item["quantity"] <= 1:
            conn.execute("DELETE FROM cart WHERE id = ?", (item_id,))
        else:
            conn.execute(
                "UPDATE cart SET quantity = quantity - 1 WHERE id = ?", (item_id,)
            )
        conn.commit()

    return jsonify({"message": "Quantity updated"}), 200


@app.route("/cart/<int:item_id>/increase", methods=["PUT"])
@login_required
def increase_quantity(item_id):
    with closing(get_db_connection()) as conn:
        conn.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE id = ? AND user_id = ?",
            (item_id, g.user_id)
        )
        conn.commit()
    return jsonify({"message": "Quantity updated"}), 200


@app.route("/orders", methods=["POST"])
@login_required
def place_order():
    data = request.get_json(silent=True) or {}
    address = (data.get("address") or "").strip()
    payment_method = (data.get("payment_method") or "").strip()

    if not address:
        return jsonify({"error": "Address is required"}), 400
    if not payment_method:
        return jsonify({"error": "Payment method is required"}), 400

    with closing(get_db_connection()) as conn:
        rows = conn.execute(
            "SELECT product_name, price, quantity, image FROM cart WHERE user_id = ?",
            (g.user_id,)
        ).fetchall()

        if not rows:
            return jsonify({"error": "Your cart is empty"}), 400

        items = [dict(row) for row in rows]
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        discount = int(subtotal * DISCOUNT_PERCENT / 100 + 0.5)
        total = subtotal - discount
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        cursor = conn.execute(
            "INSERT INTO orders (user_id, items, total, address, payment_method, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (g.user_id, json.dumps(items), total, address, payment_method, created_at)
        )
        conn.execute("DELETE FROM cart WHERE user_id = ?", (g.user_id,))
        conn.commit()
        order_id = cursor.lastrowid

    return jsonify({"message": "Order placed", "order_id": order_id, "total": total}), 201


@app.route("/orders")
@login_required
def list_orders():
    with closing(get_db_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (g.user_id,)
        ).fetchall()

    orders = []
    for row in rows:
        order = dict(row)
        order["items"] = json.loads(order["items"])
        orders.append(order)
    return jsonify(orders)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

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


@app.route("/login", methods=["POST"])
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

    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)
    token = jwt.encode(
        {"user_id": user["id"], "username": user["username"], "exp": expires},
        SECRET_KEY,
        algorithm="HS256",
    )

    return jsonify({"token": token, "username": user["username"]}), 200


if __name__ == "__main__":
    init_db()
    # threaded=True   -> handle requests concurrently.
    # use_reloader=False -> the auto-reloader restarts the app on every file
    #   save (yours or the editor's) and its half-killed processes are what
    #   kept wedging the server. Restart manually after editing app.py.
    app.run(port=5001, threaded=True, debug=False, use_reloader=False)