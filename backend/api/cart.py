from contextlib import closing

from flask import Blueprint, g, jsonify

from .auth import login_required
from .catalog import resolve_cart_item
from .db import get_db_connection
from .validation import json_body

bp = Blueprint("cart", __name__)

MAX_QUANTITY = 10              # per cart line


def get_cart_rows(conn, user_id):
    rows = conn.execute(
        "SELECT product_name, price, quantity, image FROM cart WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    return [dict(row) for row in rows]


@bp.route("/cart")
@login_required
def get_cart():
    with closing(get_db_connection()) as conn:
        items = conn.execute(
            "SELECT * FROM cart WHERE user_id = ?", (g.user_id,)
        ).fetchall()
    return jsonify([dict(item) for item in items])


@bp.route("/cart", methods=["POST"])
@login_required
def add_to_cart():
    # The client only says *what* to add; name, price and image come from
    # the catalog so they cannot be tampered with.
    data = json_body()
    product_id = data.get("product_id")
    if not isinstance(product_id, int) or isinstance(product_id, bool):
        return jsonify({"error": "product_id is required"}), 400

    variant = data.get("variant")
    if variant is not None and not isinstance(variant, str):
        return jsonify({"error": "Unknown product or variant"}), 400

    resolved = resolve_cart_item(product_id, variant)
    if resolved is None:
        return jsonify({"error": "Unknown product or variant"}), 400
    name, price, image = resolved

    with closing(get_db_connection()) as conn:
        existing = conn.execute(
            "SELECT id, quantity FROM cart WHERE product_name = ? AND user_id = ?",
            (name, g.user_id)
        ).fetchone()

        if existing:
            if existing["quantity"] >= MAX_QUANTITY:
                return jsonify({"error": f"You can add up to {MAX_QUANTITY} of an item"}), 400
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


@bp.route("/cart/<int:item_id>", methods=["DELETE"])
@login_required
def remove_from_cart(item_id):
    with closing(get_db_connection()) as conn:
        conn.execute(
            "DELETE FROM cart WHERE id = ? AND user_id = ?", (item_id, g.user_id)
        )
        conn.commit()
    return jsonify({"message": "Item removed from cart"}), 200


@bp.route("/cart/<int:item_id>/decrease", methods=["PUT"])
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


@bp.route("/cart/<int:item_id>/increase", methods=["PUT"])
@login_required
def increase_quantity(item_id):
    with closing(get_db_connection()) as conn:
        item = conn.execute(
            "SELECT quantity FROM cart WHERE id = ? AND user_id = ?",
            (item_id, g.user_id)
        ).fetchone()

        if item is None:
            return jsonify({"error": "Item not found"}), 404
        if item["quantity"] >= MAX_QUANTITY:
            return jsonify({"error": f"You can add up to {MAX_QUANTITY} of an item"}), 400

        conn.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE id = ?", (item_id,)
        )
        conn.commit()
    return jsonify({"message": "Quantity updated"}), 200
