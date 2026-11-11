import json
import os

from flask import Blueprint, jsonify

from .config import BASE_DIR

bp = Blueprint("catalog", __name__)


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


@bp.route("/products")
def list_products():
    return jsonify(PRODUCTS)
