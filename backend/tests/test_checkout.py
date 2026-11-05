import pytest

import app as app_module
from conftest import VALID_ADDRESS, make_user


@pytest.mark.parametrize(
    ("bill", "expected"),
    [(0, 0), (499, 70), (999, 70), (1000, 0), (1500, 0)],
)
def test_shipping_rule(bill, expected):
    assert app_module.shipping_for(bill) == expected


def test_prepaid_discount_does_not_apply_to_shipping():
    card = app_module.find_method("card")
    off, total = app_module.method_total(499, card)
    assert off == 25
    assert total == 499 - 25 + 70


def test_summary_for_small_cart_includes_shipping(client, auth):
    client.post("/cart", headers=auth, json={"product_id": 6, "variant": None})  # Lip Mask, 399
    summary = client.get("/checkout/summary", headers=auth).get_json()

    assert summary["subtotal"] == 399
    assert summary["bill_total"] == 399 - 80            # 20% off, rounded
    assert summary["shipping"] == 70
    assert summary["free_shipping"] is False
    cod = next(m for m in summary["methods"] if m["id"] == "cod")
    assert cod["total"] == summary["bill_total"] + 70


# ---- Addresses ----
def test_address_validation(client, auth):
    assert client.post("/addresses", headers=auth, json=VALID_ADDRESS).status_code == 201
    for field, bad in [("mobile", "12345"), ("pincode", "012345"), ("state", "Atlantis"),
                       ("type", "Castle"), ("full_name", "x" * 61)]:
        response = client.post("/addresses", headers=auth, json={**VALID_ADDRESS, field: bad})
        assert response.status_code == 400, field


def test_addresses_are_private(client, auth):
    address_id = client.post("/addresses", headers=auth, json=VALID_ADDRESS).get_json()["id"]
    bob = make_user(client, "bob")

    assert client.get("/addresses", headers=bob).get_json() == []
    assert client.put(f"/addresses/{address_id}", headers=bob, json=VALID_ADDRESS).status_code == 404


# ---- Orders ----
def place(client, headers, **overrides):
    body = {"address_id": None, "payment_method": "cod", "payment_option": "", "gifts": []}
    body.update(overrides)
    return client.post("/orders", headers=headers, json=body)


def test_order_flow(client, auth):
    address_id = client.post("/addresses", headers=auth, json=VALID_ADDRESS).get_json()["id"]
    assert place(client, auth, address_id=address_id).status_code == 400   # empty cart

    client.post("/cart", headers=auth, json={"product_id": 6, "variant": None})
    response = place(client, auth, address_id=address_id)
    assert response.status_code == 201
    assert response.get_json()["total"] == 319 + 70

    assert client.get("/cart", headers=auth).get_json() == []
    [order] = client.get("/orders", headers=auth).get_json()
    assert order["total"] == 319 + 70
    assert order["items"][0]["product_name"] == "Lip Mask"


def test_order_rejects_bad_input(client, auth):
    address_id = client.post("/addresses", headers=auth, json=VALID_ADDRESS).get_json()["id"]
    client.post("/cart", headers=auth, json={"product_id": 6, "variant": None})

    assert place(client, auth).status_code == 400                                         # no address
    assert place(client, auth, address_id=address_id, payment_method="bitcoin").status_code == 400
    assert place(client, auth, address_id=address_id, payment_method="card",
                 payment_option="Monopoly Money").status_code == 400
    # Bill is below the first free-gift threshold, so no gifts are allowed.
    assert place(client, auth, address_id=address_id,
                 gifts=[app_module.FREE_GIFTS[0]["name"]]).status_code == 400

    bob = make_user(client, "bob")
    client.post("/cart", headers=bob, json={"product_id": 6, "variant": None})
    assert place(client, bob, address_id=address_id).status_code == 400   # not bob's address
