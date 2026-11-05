import re
from contextlib import closing

from flask import Blueprint, g, jsonify, request

from .auth import login_required
from .db import get_db_connection

bp = Blueprint("addresses", __name__)

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
ADDRESS_MAX_LENGTHS = {
    "full_name": 60, "flat": 120, "area": 120, "landmark": 120, "city": 60,
}


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

    for key, limit in ADDRESS_MAX_LENGTHS.items():
        if len(cleaned[key]) > limit:
            return None, f"{key.replace('_', ' ').capitalize()} is too long (max {limit} characters)"

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


@bp.route("/addresses")
@login_required
def list_addresses():
    with closing(get_db_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM addresses WHERE user_id = ? ORDER BY id DESC",
            (g.user_id,)
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@bp.route("/addresses", methods=["POST"])
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


@bp.route("/addresses/<int:address_id>", methods=["PUT"])
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


@bp.route("/addresses/<int:address_id>", methods=["DELETE"])
@login_required
def delete_address(address_id):
    with closing(get_db_connection()) as conn:
        conn.execute(
            "DELETE FROM addresses WHERE id = ? AND user_id = ?",
            (address_id, g.user_id)
        )
        conn.commit()
    return jsonify({"message": "Address deleted"}), 200
