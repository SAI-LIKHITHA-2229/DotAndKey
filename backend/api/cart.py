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
    has left the catalog are skipped. This only reads, so viewing a cart
    never changes it.
    """
    rows = conn.execute(
        "SELECT id, product_id, variant, quantity FROM cart WHERE user_id = %s ORDER BY id",
        (user_id,)
    ).fetchall()

    lines = []
    for row in rows:
        resolved = resolve_cart_item(row["product_id"], row["variant"] or None)
        if resolved is None:
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
    return lines


@bp.route("/cart")
@login_required
def get_cart():
    with closing(get_db_connection()) as conn:
        lines = cart_lines(conn, g.user_id)
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
        # One statement, so two quick clicks can't both pass the limit:
        # add the line, or raise its quantity if it is still below the limit.
        saved = conn.execute(
            "INSERT INTO cart (user_id, product_id, variant, quantity) VALUES (%s, %s, %s, 1) "
            "ON CONFLICT (user_id, product_id, variant) DO UPDATE "
            "SET quantity = cart.quantity + 1 WHERE cart.quantity < %s "
            "RETURNING id",
            (g.user_id, product_id, variant or "", MAX_QUANTITY)
        ).fetchone()
        if saved is None:
            return jsonify({"error": f"You can add up to {MAX_QUANTITY} of an item"}), 400
        conn.commit()

    return jsonify({"message": "Item added to cart"}), 201


@bp.route("/cart/<int:item_id>", methods=["DELETE"])
@login_required
def remove_from_cart(item_id):
    with closing(get_db_connection()) as conn:
        conn.execute(
            "DELETE FROM cart WHERE id = %s AND user_id = %s", (item_id, g.user_id)
        )
        conn.commit()
    return jsonify({"message": "Item removed from cart"}), 200


@bp.route("/cart/<int:item_id>/decrease", methods=["PUT"])
@login_required
def decrease_quantity(item_id):
    with closing(get_db_connection()) as conn:
        reduced = conn.execute(
            "UPDATE cart SET quantity = quantity - 1 "
            "WHERE id = %s AND user_id = %s AND quantity > 1",
            (item_id, g.user_id)
        )
        if reduced.rowcount == 0:
            # Quantity was 1 (remove the line) or the line doesn't exist.
            removed = conn.execute(
                "DELETE FROM cart WHERE id = %s AND user_id = %s", (item_id, g.user_id)
            )
            if removed.rowcount == 0:
                return jsonify({"error": "Item not found"}), 404
        conn.commit()

    return jsonify({"message": "Quantity updated"}), 200


@bp.route("/cart/<int:item_id>/increase", methods=["PUT"])
@login_required
def increase_quantity(item_id):
    with closing(get_db_connection()) as conn:
        raised = conn.execute(
            "UPDATE cart SET quantity = quantity + 1 "
            "WHERE id = %s AND user_id = %s AND quantity < %s",
            (item_id, g.user_id, MAX_QUANTITY)
        )
        if raised.rowcount == 0:
            # Nothing changed: either the line doesn't exist or it is at the limit.
            exists = conn.execute(
                "SELECT 1 FROM cart WHERE id = %s AND user_id = %s", (item_id, g.user_id)
            ).fetchone()
            if exists is None:
                return jsonify({"error": "Item not found"}), 404
            return jsonify({"error": f"You can add up to {MAX_QUANTITY} of an item"}), 400
        conn.commit()
    return jsonify({"message": "Quantity updated"}), 200
