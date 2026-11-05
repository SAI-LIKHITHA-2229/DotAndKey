import datetime
import json
import logging
import os
import re
import sqlite3
from contextlib import closing
from functools import wraps

import jwt
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log = logging.getLogger(__name__)

# ---- Configuration (override with environment variables) ----
APP_ENV = os.environ.get("APP_ENV", "development")
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "cart.db"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
TOKEN_HOURS = 12

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if APP_ENV == "production":
        raise RuntimeError("SECRET_KEY must be set in production")
    SECRET_KEY = "dev-only-insecure-key-change-me-in-production"
    log.warning("SECRET_KEY not set; using an insecure development key")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024   # requests are small JSON bodies
CORS(app, origins=CORS_ORIGINS)

# ---- Pricing rules (the server is the only place these are decided) ----
DISCOUNT_PERCENT = 20          # store-wide discount
PREPAID_EXTRA_PERCENT = 5      # extra off for card / wallet / netbanking
FREE_SHIPPING_MIN = 1000       # bill needed for free shipping
SHIPPING_FEE = 70              # charged when the bill is below FREE_SHIPPING_MIN
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

# ---- Address rules ----
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
]
ADDRESS_TYPES = ["Home", "Work", "Other"]
MAX_ADDRESSES = 10


# ---- Product catalog (the server decides names, prices and images) ----
def load_catalog():
    with open(os.path.join(BASE_DIR, "products.json"), encoding="utf-8") as f:
        return json.load(f)


PRODUCTS = load_catalog()
PRODUCTS_BY_ID = {product["id"]: product for product in PRODUCTS}


def resolve_cart_item(product_id, variant_label):
    """Return (name, price, image) for a catalog item, or None if invalid."""
    product = PRODUCTS_BY_ID.get(product_id)
    if product is None:
        return None

    variants = product.get("variants") or []
    if not variants:
        # Products without variants are added without a label.
        if variant_label:
            return None
        return product["name"], product["price"], product["image"]

    variant = next((v for v in variants if v["label"] == variant_label), None)
    if variant is None:
        return None
    name = f"{product['name']} ({variant['label']})"
    return name, product["price"], variant.get("image") or product["image"]


def get_db_connection():
    # timeout / busy_timeout: wait for a lock instead of failing or hanging.
    conn = sqlite3.connect(DATABASE_PATH, timeout=10)
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                mobile TEXT NOT NULL,
                pincode TEXT NOT NULL,
                flat TEXT NOT NULL,
                area TEXT NOT NULL,
                landmark TEXT,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                type TEXT NOT NULL
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


def shipping_for(bill_total):
    # An empty cart has nothing to ship.
    if bill_total == 0 or bill_total >= FREE_SHIPPING_MIN:
        return 0
    return SHIPPING_FEE


def method_total(bill_total, method):
    # The prepaid discount applies to the products only, not to shipping.
    off = percent_of(bill_total, PREPAID_EXTRA_PERCENT) if method["prepaid"] else 0
    return off, bill_total - off + shipping_for(bill_total)


def find_method(method_id):
    for method in PAYMENT_METHODS:
        if method["id"] == method_id:
            return method
    return None


# ---- Address helpers ----
def clean_address(data):
    """Return (cleaned_dict, error_message). Exactly one of them is None."""
    def text(key):
        value = data.get(key)
        return value.strip() if isinstance(value, str) else ""

    cleaned = {
        "full_name": text("full_name"),
        "mobile": text("mobile"),
        "pincode": text("pincode"),
        "flat": text("flat"),
        "area": text("area"),
        "landmark": text("landmark"),
        "city": text("city"),
        "state": text("state"),
        "type": text("type") or "Home",
    }

    if len(cleaned["full_name"]) < 2:
        return None, "Enter your full name"
    if not re.fullmatch(r"[6-9]\d{9}", cleaned["mobile"]):
        return None, "Enter a valid 10-digit mobile number"
    if not re.fullmatch(r"[1-9]\d{5}", cleaned["pincode"]):
        return None, "Enter a valid 6-digit PIN code"
    if not cleaned["flat"]:
        return None, "Enter your flat / house number"
    if not cleaned["area"]:
        return None, "Enter your area / street"
    if not cleaned["city"]:
        return None, "Enter your city"
    if cleaned["state"] not in INDIAN_STATES:
        return None, "Choose a state"
    if cleaned["type"] not in ADDRESS_TYPES:
        return None, "Choose an address type"

    return cleaned, None


def address_to_text(address):
    parts = [address["full_name"], address["flat"], address["area"]]
    if address["landmark"]:
        parts.append(address["landmark"])
    parts.append(address["city"])
    parts.append(f"{address['state']} - {address['pincode']}")
    return ", ".join(parts) + f" · Phone: {address['mobile']}"


# ---- Errors: always answer with JSON, never an HTML error page ----
@app.errorhandler(HTTPException)
def handle_http_error(error):
    return jsonify({"error": error.description}), error.code


@app.errorhandler(Exception)
def handle_unexpected_error(_error):
    log.exception("Unhandled error")
    return jsonify({"error": "Something went wrong on our side"}), 500


# ---- Health and catalog (public) ----
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/products")
def list_products():
    return jsonify(PRODUCTS)


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
    # The client only says *what* to add; name, price and image come from
    # the catalog so they cannot be tampered with.
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    if not isinstance(product_id, int) or isinstance(product_id, bool):
        return jsonify({"error": "product_id is required"}), 400

    resolved = resolve_cart_item(product_id, data.get("variant"))
    if resolved is None:
        return jsonify({"error": "Unknown product or variant"}), 400
    name, price, image = resolved

    with closing(get_db_connection()) as conn:
        existing = conn.execute(
            "SELECT id FROM cart WHERE product_name = ? AND user_id = ?",
            (name, g.user_id)
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
                (name, price, 1, image, g.user_id)
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


# ---- Addresses ----
@app.route("/addresses")
@login_required
def list_addresses():
    with closing(get_db_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM addresses WHERE user_id = ? ORDER BY id DESC",
            (g.user_id,)
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/addresses", methods=["POST"])
@login_required
def add_address():
    data = request.get_json(silent=True) or {}
    cleaned, error = clean_address(data)
    if error:
        return jsonify({"error": error}), 400

    with closing(get_db_connection()) as conn:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM addresses WHERE user_id = ?", (g.user_id,)
        ).fetchone()["n"]
        if count >= MAX_ADDRESSES:
            return jsonify({"error": f"You can save up to {MAX_ADDRESSES} addresses"}), 400

        cursor = conn.execute(
            "INSERT INTO addresses (user_id, full_name, mobile, pincode, flat, "
            "area, landmark, city, state, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (g.user_id, cleaned["full_name"], cleaned["mobile"], cleaned["pincode"],
             cleaned["flat"], cleaned["area"], cleaned["landmark"], cleaned["city"],
             cleaned["state"], cleaned["type"])
        )
        conn.commit()
        new_id = cursor.lastrowid

    return jsonify({"message": "Address saved", "id": new_id}), 201


@app.route("/addresses/<int:address_id>", methods=["PUT"])
@login_required
def update_address(address_id):
    data = request.get_json(silent=True) or {}
    cleaned, error = clean_address(data)
    if error:
        return jsonify({"error": error}), 400

    with closing(get_db_connection()) as conn:
        cursor = conn.execute(
            "UPDATE addresses SET full_name = ?, mobile = ?, pincode = ?, flat = ?, "
            "area = ?, landmark = ?, city = ?, state = ?, type = ? "
            "WHERE id = ? AND user_id = ?",
            (cleaned["full_name"], cleaned["mobile"], cleaned["pincode"],
             cleaned["flat"], cleaned["area"], cleaned["landmark"], cleaned["city"],
             cleaned["state"], cleaned["type"], address_id, g.user_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Address not found"}), 404

    return jsonify({"message": "Address updated"}), 200


@app.route("/addresses/<int:address_id>", methods=["DELETE"])
@login_required
def delete_address(address_id):
    with closing(get_db_connection()) as conn:
        conn.execute(
            "DELETE FROM addresses WHERE id = ? AND user_id = ?",
            (address_id, g.user_id)
        )
        conn.commit()
    return jsonify({"message": "Address deleted"}), 200


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
        "shipping": shipping_for(bill_total),
        "shipping_fee": SHIPPING_FEE,
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
    address_id = data.get("address_id")
    method = find_method(data.get("payment_method"))
    option = (data.get("payment_option") or "").strip()
    chosen_gifts = data.get("gifts") or []

    if not isinstance(address_id, int) or isinstance(address_id, bool):
        return jsonify({"error": "Choose a delivery address"}), 400
    if method is None:
        return jsonify({"error": "Choose a payment method"}), 400
    if method["options"] and option not in method["options"]:
        return jsonify({"error": "Choose an option for this payment method"}), 400

    with closing(get_db_connection()) as conn:
        # Only this user's own addresses can be used.
        address_row = conn.execute(
            "SELECT * FROM addresses WHERE id = ? AND user_id = ?",
            (address_id, g.user_id)
        ).fetchone()
        if address_row is None:
            return jsonify({"error": "Delivery address not found"}), 400
        address_text = address_to_text(dict(address_row))

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
            (g.user_id, json.dumps(items + gift_items), total, address_text,
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

    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=TOKEN_HOURS)
    token = jwt.encode(
        {"user_id": user["id"], "username": user["username"], "exp": expires},
        SECRET_KEY,
        algorithm="HS256",
    )

    return jsonify({"token": token, "username": user["username"]}), 200


# Create tables on startup, however the app is launched
# (python app.py, flask run, gunicorn or the test suite).
init_db()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # threaded=True   -> handle requests concurrently.
    # use_reloader=False -> the auto-reloader restarts the app on every file
    #   save (yours or the editor's) and its half-killed processes are what
    #   kept wedging the server. Restart manually after editing app.py.
    app.run(port=int(os.environ.get("PORT", 5001)), threaded=True,
            debug=False, use_reloader=False)