from contextlib import closing

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

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

        # Migrate older databases created before the "image" column existed.
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(cart)")]
        if "image" not in columns:
            conn.execute("ALTER TABLE cart ADD COLUMN image TEXT")

        conn.commit()

@app.route("/cart")
def get_cart():
    with closing(get_db_connection()) as conn:
        items = conn.execute("SELECT * FROM cart").fetchall()
    return jsonify([dict(item) for item in items])

@app.route("/cart", methods=["POST"])
def add_to_cart():
    new_item = request.get_json(silent=True) or {}
    if not new_item.get("product_name"):
        return jsonify({"error": "product_name is required"}), 400

    with closing(get_db_connection()) as conn:
        existing = conn.execute(
            "SELECT id FROM cart WHERE product_name = ?",
            (new_item["product_name"],)
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE cart SET quantity = quantity + 1 WHERE id = ?",
                (existing["id"],)
            )
        else:
            conn.execute(
                "INSERT INTO cart (product_name, price, quantity, image) VALUES (?, ?, ?, ?)",
                (new_item["product_name"], new_item.get("price", 0), 1, new_item.get("image"))
            )
        conn.commit()

    return jsonify({"message": "Item added to cart"}), 201

@app.route("/cart/<int:item_id>", methods=["DELETE"])
def remove_from_cart(item_id):
    with closing(get_db_connection()) as conn:
        conn.execute("DELETE FROM cart WHERE id = ?", (item_id,))
        conn.commit()
    return jsonify({"message": "Item removed from cart"}), 200

@app.route("/cart/<int:item_id>/decrease", methods=["PUT"])
def decrease_quantity(item_id):
    with closing(get_db_connection()) as conn:
        item = conn.execute(
            "SELECT quantity FROM cart WHERE id = ?", (item_id,)
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
def increase_quantity(item_id):
    with closing(get_db_connection()) as conn:
        conn.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE id = ?", (item_id,)
        )
        conn.commit()
    return jsonify({"message": "Quantity updated"}), 200

if __name__ == "__main__":
    init_db()
    # threaded=True   -> handle requests concurrently.
    # use_reloader=False -> the auto-reloader restarts the app on every file
    #   save (yours or the editor's) and its half-killed processes are what
    #   kept wedging the server. Restart manually after editing app.py.
    app.run(port=5001, threaded=True, debug=False, use_reloader=False)
