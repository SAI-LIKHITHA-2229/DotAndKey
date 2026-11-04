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

# ---- Pricing rules (the server is the only place these are decided) ----
DISCOUNT_PERCENT = 20          # store-wide discount
PREPAID_EXTRA_PERCENT = 5      # extra off for card / wallet / netbanking
FREE_SHIPPING_MIN = 1000       # bill needed for free shipping
FREE_GIFT_STEP = 1000          # one free gift per this much

FREE_GIFTS = [
    {"name": "Vitamin C Facewash - 15ml", "image": "gift-vitc-facewash.jpg"},
    {"name": "72HR Hydrating Gel Moisturizer - 15ml", "image": "gift-72hr-moisturizer.jpg"},
    {"name": "Barrier Repair Moisturizer - 15ml", "image": "gift-barrier-repair.jpg"},
    {"name": "Strawberry Moisturizer - 15ml", "image": "gift-strawberry-moisturizer.jpg"},
    {"name": "CICA + Niacinamide Oil Free Moisturizer - 15ml", "image": "gift-cica-niacinamide.jpg"},
]

PAYMENT_METHODS = [
    {"id": "cod", "title": "Cash on delivery", "sub": "Pay with cash",
     "prepaid": False, "options": []},
    {"id": "card", "title": "Debit/Credit cards", "sub": "Visa, Mastercard, RuPay & more",
     "prepaid": True, "options": ["Visa", "Mastercard", "RuPay", "American Express"]},
    {"id": "wallet", "title": "Wallets", "sub": "Amazon Pay, PhonePe, Mobikwik & more",
     "prepaid": True, "options": ["Amazon Pay", "PhonePe", "Mobikwik"]},
    {"id": "netbanking", "title": "Netbanking", "sub": "Select from a list of banks",
     "prepaid": True,
     "options": ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank",
                 "Kotak Mahindra Bank", "Punjab National Bank", "Bank of Baroda",
                 "Yes Bank"]},
    {"id": "paylater", "title": "Pay Later", "sub": "LazyPay, Simpl & more",
     "prepaid": False, "options": ["LazyPay", "Simpl", "ICICI PayLater"]},
]


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


# ---- Pricing helpers ----
def percent_of(amount, percent):
    return int(amount * percent / 100 + 0.5)


def get_cart_rows(conn, user_id):
    rows = conn.execute(
        "SELECT product_name, price, quantity, image FROM cart WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    return [dict(row) for row in rows]


def price_cart(items):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    discount = percent_of(subtotal, DISCOUNT_PERCENT)
    return subtotal, discount, subtotal - discount


def max_gifts_for(bill_total):
    return min(bill_total // FREE_GIFT_STEP, len(FREE_GIFTS))


def method_total(bill_total, method):
    off = percent_of(bill_total, PREPAID_EXTRA_PERCENT) if method["prepaid"] else 0
    return off, bill_total - off


def find_method(method_id):
    for method in PAYMENT_METHODS:
        if method["id"] == method_id:
            return method
    return None


# ---- Cart ----
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


# ---- Checkout ----
@app.route("/checkout/summary")
@login_required
def checkout_summary():
    with closing(get_db_connection()) as conn:
        items = get_cart_rows(conn, g.user_id)

    subtotal, discount, bill_total = price_cart(items)
    max_gifts = max_gifts_for(bill_total)

    methods = []
    for method in PAYMENT_METHODS:
        off, total = method_total(bill_total, method)
        methods.append({**method, "discount": off, "total": total})

    return jsonify({
        "subtotal": subtotal,
        "discount": discount,
        "discount_percent": DISCOUNT_PERCENT,
        "bill_total": bill_total,
        "free_shipping": bill_total >= FREE_SHIPPING_MIN,
        "free_shipping_remaining": max(0, FREE_SHIPPING_MIN - bill_total),
        "prepaid_percent": PREPAID_EXTRA_PERCENT,
        "gifts": {
            "available": FREE_GIFTS,
            "max": max_gifts,
            "all_unlocked": max_gifts >= len(FREE_GIFTS),
            "next_unlock_in": FREE_GIFT_STEP - (bill_total % FREE_GIFT_STEP),
        },
        "methods": methods,
    })


@app.route("/orders", methods=["POST"])
@login_required
def place_order():
    data = request.get_json(silent=True) or {}
    address = (data.get("address") or "").strip()
    method = find_method(data.get("payment_method"))
    option = (data.get("payment_option") or "").strip()
    chosen_gifts = data.get("gifts") or []

    if not address:
        return jsonify({"error": "Address is required"}), 400
    if method is None:
        return jsonify({"error": "Choose a payment method"}), 400
    if method["options"] and option not in method["options"]:
        return jsonify({"error": "Choose an option for this payment method"}), 400

    with closing(get_db_connection()) as conn:
        items = get_cart_rows(conn, g.user_id)
        if not items:
            return jsonify({"error": "Your cart is empty"}), 400

        subtotal, discount, bill_total = price_cart(items)
        max_gifts = max_gifts_for(bill_total)

        if max_gifts >= len(FREE_GIFTS):
            gifts = list(FREE_GIFTS)
        else:
            gift_lookup = {gift["name"]: gift for gift in FREE_GIFTS}
            valid = (
                isinstance(chosen_gifts, list)
                and all(isinstance(name, str) for name in chosen_gifts)
                and len(set(chosen_gifts)) == len(chosen_gifts)
                and len(chosen_gifts) <= max_gifts
                and all(name in gift_lookup for name in chosen_gifts)
            )
            if not valid:
                return jsonify({"error": "Invalid free gift selection"}), 400
            gifts = [gift_lookup[name] for name in chosen_gifts]

        gift_items = [
            {
                "product_name": f"{gift['name']} (Free gift)",
                "price": 0,
                "quantity": 1,
                "image": gift["image"],
            }
            for gift in gifts
        ]

        _, total = method_total(bill_total, method)
        payment_text = method["title"] + (f" · {option}" if option else "")
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        cursor = conn.execute(
            "INSERT INTO orders (user_id, items, total, address, payment_method, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (g.user_id, json.dumps(items + gift_items), total, address,
             payment_text, created_at)
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


# ---- Accounts ----
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