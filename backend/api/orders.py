from collections import defaultdict
from contextlib import closing

from flask import Blueprint, g, jsonify

from .addresses import ADDRESS_COLUMNS, address_to_text
from .auth import login_required
from .cart import cart_lines
from .db import get_db_connection
from .pricing import (
    DISCOUNT_PERCENT, FREE_GIFT_STEP, FREE_GIFTS, FREE_SHIPPING_MIN, PAYMENT_METHODS,
    PREPAID_EXTRA_PERCENT, SHIPPING_FEE, find_method, max_gifts_for, method_total,
    price_cart, shipping_for,
)
from .validation import json_body, text_field

bp = Blueprint("orders", __name__)

# Orders start "confirmed"; a fulfilment system would move them to
# "shipped" and "delivered". Prepaid methods use a demo payment step (no
# money is taken), recorded honestly as "demo_paid"; cash on delivery and
# pay later stay "pending" until the customer pays. The orders table only
# accepts known status values.


@bp.route("/checkout/summary")
@login_required
def checkout_summary():
    with closing(get_db_connection()) as conn:
        items = cart_lines(conn, g.user_id)

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


@bp.route("/orders", methods=["POST"])
@login_required
def place_order():
    data = json_body()
    address_id = data.get("address_id")
    method = find_method(text_field(data, "payment_method"))
    option = text_field(data, "payment_option")
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
            f"SELECT {ADDRESS_COLUMNS} FROM addresses WHERE id = %s AND user_id = %s",
            (address_id, g.user_id)
        ).fetchone()
        if address_row is None:
            return jsonify({"error": "Delivery address not found"}), 400
        address_text = address_to_text(dict(address_row))

        # Snapshot the current catalog price: the order keeps what was paid
        # even if the catalog changes later.
        items = [
            {key: line[key] for key in ("product_name", "price", "quantity", "image")}
            for line in cart_lines(conn, g.user_id)
        ]
        if not items:
            return jsonify({"error": "Your cart is empty"}), 400

        _, _, bill_total = price_cart(items)
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
        payment_status = "demo_paid" if method["prepaid"] else "pending"

        order_id = conn.execute(
            "INSERT INTO orders (user_id, total, address, payment_method, "
            "payment_status, status) VALUES (%s, %s, %s, %s, %s, 'confirmed') "
            "RETURNING id",
            (g.user_id, total, address_text, payment_text, payment_status)
        ).fetchone()["id"]
        with conn.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO order_items (order_id, product_name, price, quantity, image) "
                "VALUES (%s, %s, %s, %s, %s)",
                [(order_id, item["product_name"], item["price"], item["quantity"], item["image"])
                 for item in items + gift_items]
            )
        conn.execute("DELETE FROM cart WHERE user_id = %s", (g.user_id,))
        conn.commit()

    return jsonify({"message": "Order placed", "order_id": order_id, "total": total,
                    "status": "confirmed", "payment_status": payment_status}), 201


@bp.route("/orders")
@login_required
def list_orders():
    with closing(get_db_connection()) as conn:
        orders = conn.execute(
            "SELECT id, total, address, payment_method, status, payment_status, "
            "created_at FROM orders WHERE user_id = %s ORDER BY id DESC",
            (g.user_id,)
        ).fetchall()
        # One query for every item, instead of one query per order.
        item_rows = conn.execute(
            "SELECT i.order_id, i.product_name, i.price, i.quantity, i.image "
            "FROM order_items i JOIN orders o ON o.id = i.order_id "
            "WHERE o.user_id = %s ORDER BY i.id",
            (g.user_id,)
        ).fetchall()

    items_by_order = defaultdict(list)
    for item in item_rows:
        items_by_order[item.pop("order_id")].append(item)

    for order in orders:
        order["items"] = items_by_order[order["id"]]
        order["created_at"] = order["created_at"].isoformat()
    return jsonify(orders)
