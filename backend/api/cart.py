from contextlib import closing

from flask import Blueprint, g, jsonify

from .auth import login_required
from .catalog import resolve_cart_item
from .db import get_db_connection
from .validation import json_body

bp = Blueprint("cart", __name__)

MAX_QUANTITY = 10              # per cart line


def cart_lines(conn, user_id):
    """The user's cart with names, prices and images taken from the catalog.

    The database only stores product_id, variant and quantity, so prices are
    always current and can never be set by the client. Lines whose product
    has left the catalog are deleted; the caller commits, so this is safe to
    use inside a larger transaction such as placing an order.
    """
    rows = conn.execute(
        "SELECT id, product_id, variant, quantity FROM cart WHERE user_id = ? ORDER BY id",
        (user_id,)
    ).fetchall()

    lines, gone = [], []
    for row in rows:
        resolved = resolve_cart_item(row["product_id"], row["variant"] or None)
        if resolved is None:
            gone.append(row["id"])
            continue
        name, price, image = resolved
        lines.append({
            "id": row["id"],
            "product_id": row["product_id"],
            "variant": row["variant"] or None,
            "product_name": name,
            "price": price,
            "image": image,
            "quantity": row["quantity"],
        })

    if gone:
        conn.executemany("DELETE FROM cart WHERE id = ?", [(item_id,) for item_id in gone])
    return lines


@bp.route("/cart")
@login_required
def get_cart():
    with closing(get_db_connection()) as conn:
        lines = cart_lines(conn, g.user_id)
        conn.commit()
    return jsonify(lines)


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

    if resolve_cart_item(product_id, variant) is None:
        return jsonify({"error": "Unknown product or variant"}), 400

    with closing(get_db_connection()) as conn:
        existing = conn.execute(
            "SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ? AND variant = ?",
            (g.user_id, product_id, variant or "")
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
                "INSERT INTO cart (user_id, product_id, variant, quantity) VALUES (?, ?, ?, 1)",
                (g.user_id, product_id, variant or "")
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
