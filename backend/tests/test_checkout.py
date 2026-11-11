import threading

import pytest

from api import pricing
from api.addresses import MAX_ADDRESSES
from conftest import (
    VALID_ADDRESS, connect_to_test_database, make_user, requests_at_once, run_at_once,
)

LIP_MASK = {"product_id": 6, "variant": None}
MOISTURIZER_VARIANT = "Watermelon Cooling Gel"
MOISTURIZER = {"product_id": 1, "variant": MOISTURIZER_VARIANT}


@pytest.mark.parametrize(
    ("bill", "expected"),
    [(0, 0), (499, 70), (999, 70), (1000, 0), (1500, 0)],
)
def test_shipping_rule(bill, expected):
    assert pricing.shipping_for(bill) == expected


def test_prepaid_discount_does_not_apply_to_shipping():
    card = pricing.find_method("card")
    off, total = pricing.method_total(499, card)
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


def test_simultaneous_saves_never_pass_the_address_limit(app, client, auth):
    codes = requests_at_once(
        app, MAX_ADDRESSES + 6, lambda c: c.post("/addresses", headers=auth, json=VALID_ADDRESS)
    )

    assert sorted(codes) == [201] * MAX_ADDRESSES + [400] * 6
    assert len(client.get("/addresses", headers=auth).get_json()) == MAX_ADDRESSES


# ---- Orders ----
def place(client, headers, **overrides):
    body = {"address_id": None, "payment_method": "cod", "payment_option": "", "gifts": []}
    body.update(overrides)
    return client.post("/orders", headers=headers, json=body)


def test_order_flow(client, auth):
    address_id = client.post("/addresses", headers=auth, json=VALID_ADDRESS).get_json()["id"]
    assert place(client, auth, address_id=address_id).status_code == 400   # empty cart
    assert client.get("/orders", headers=auth).get_json() == []

    client.post("/cart", headers=auth, json={"product_id": 6, "variant": None})
    response = place(client, auth, address_id=address_id)
    assert response.status_code == 201
    assert response.get_json()["total"] == 319 + 70

    assert client.get("/cart", headers=auth).get_json() == []
    [order] = client.get("/orders", headers=auth).get_json()
    assert order["total"] == 319 + 70
    assert order["items"][0]["product_name"] == "Lip Mask"
    assert order["status"] == "confirmed"
    assert order["payment_status"] == "pending"          # cash on delivery
    assert "user_id" not in order
    assert "user_id" not in client.get("/addresses", headers=auth).get_json()[0]
    # The exact shape the Account page reads.
    assert set(order) == {"id", "items", "total", "address", "payment_method",
                          "status", "payment_status", "created_at"}
    assert set(order["items"][0]) == {"product_name", "price", "quantity", "image"}
    assert (order["items"][0]["price"], order["items"][0]["quantity"]) == (399, 1)


def test_order_items_stay_in_order_with_gifts_last(client, auth):
    address_id = client.post("/addresses", headers=auth, json=VALID_ADDRESS).get_json()["id"]
    for _ in range(4):
        client.post("/cart", headers=auth, json={"product_id": 6, "variant": None})

    response = place(client, auth, address_id=address_id, gifts=[pricing.FREE_GIFTS[0]["name"]])
    assert response.status_code == 201

    [order] = client.get("/orders", headers=auth).get_json()
    assert order["items"][0]["product_name"] == "Lip Mask"
    assert order["items"][0]["quantity"] == 4
    assert order["items"][-1]["product_name"].endswith("(Free gift)")


# ---- Stock ----
def stock_of(product_id=6, variant=""):
    with connect_to_test_database() as conn:
        return conn.execute(
            "SELECT quantity FROM inventory WHERE product_id = %s AND variant = %s",
            (product_id, variant),
        ).fetchone()["quantity"]


def set_stock(quantity, product_id=6, variant=""):
    with connect_to_test_database() as conn:
        conn.execute(
            "UPDATE inventory SET quantity = %s WHERE product_id = %s AND variant = %s",
            (quantity, product_id, variant),
        )


def count_rows(table):
    with connect_to_test_database() as conn:
        return conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]


def shopper(client, name, products=(LIP_MASK,)):
    """A new user with a saved address and the given products in the cart."""
    headers = make_user(client, name)
    address_id = client.post("/addresses", headers=headers, json=VALID_ADDRESS).get_json()["id"]
    for product in products:
        client.post("/cart", headers=headers, json=product)
    return headers, address_id


def checkouts_at_once(app, shoppers):
    """Every shopper presses "place order" at the same moment."""
    start_together = threading.Barrier(len(shoppers))

    def checkout(index):
        headers, address_id = shoppers[index]
        with app.test_client() as client:
            start_together.wait(timeout=10)
            return place(client, headers, address_id=address_id).status_code

    return run_at_once(len(shoppers), checkout)


def test_an_order_reduces_stock(client):
    headers, address_id = shopper(client, "alice")
    client.post("/cart", headers=headers, json=LIP_MASK)     # quantity 2

    assert place(client, headers, address_id=address_id).status_code == 201
    assert stock_of() == 98


def test_an_order_for_more_than_is_left_is_refused(client):
    headers, address_id = shopper(client, "alice")
    client.post("/cart", headers=headers, json=LIP_MASK)     # quantity 2
    set_stock(1)

    response = place(client, headers, address_id=address_id)

    assert response.status_code == 409
    assert response.get_json()["error"] == "Only 1 left of Lip Mask"
    assert stock_of() == 1
    assert count_rows("orders") == 0
    assert len(client.get("/cart", headers=headers).get_json()) == 1   # the cart is kept


def test_a_refused_order_takes_no_stock_at_all(client):
    """The first item is available and the second isn't: nothing may change."""
    headers, address_id = shopper(client, "alice", (MOISTURIZER, LIP_MASK))
    set_stock(0)

    response = place(client, headers, address_id=address_id)

    assert response.status_code == 409
    assert response.get_json()["error"] == "Lip Mask is out of stock"
    assert stock_of(1, MOISTURIZER_VARIANT) == 100


@pytest.mark.parametrize("attempt", range(5))
def test_two_simultaneous_checkouts_of_the_last_unit_exactly_one_wins(app, client, attempt):
    shoppers = [shopper(client, "alice"), shopper(client, "bob")]
    set_stock(1)

    codes = checkouts_at_once(app, shoppers)

    assert sorted(codes) == [201, 409]
    assert stock_of() == 0
    assert count_rows("orders") == 1
    assert count_rows("cart") == 1      # the loser still has their cart


def test_double_submit_by_one_user_places_one_order(app, client):
    headers, address_id = shopper(client, "alice")

    codes = checkouts_at_once(app, [(headers, address_id), (headers, address_id)])

    assert sorted(codes) == [201, 400]  # the second finds the cart empty
    assert stock_of() == 99
    assert count_rows("orders") == 1


def test_carts_filled_in_opposite_orders_cannot_deadlock(app, client):
    shoppers = [
        shopper(client, f"shopper{number}",
                (MOISTURIZER, LIP_MASK) if number % 2 else (LIP_MASK, MOISTURIZER))
        for number in range(6)
    ]

    assert checkouts_at_once(app, shoppers) == [201] * 6
    assert stock_of() == 94
    assert stock_of(1, MOISTURIZER_VARIANT) == 94


def test_prepaid_orders_are_marked_as_demo_payments(client, auth):
    address_id = client.post("/addresses", headers=auth, json=VALID_ADDRESS).get_json()["id"]
    client.post("/cart", headers=auth, json={"product_id": 6, "variant": None})

    response = place(client, auth, address_id=address_id, payment_method="card",
                     payment_option="Visa")
    assert response.status_code == 201
    assert response.get_json()["payment_status"] == "demo_paid"
    assert response.get_json()["total"] == 319 - 16 + 70  # 5% prepaid off, then shipping


def test_order_rejects_bad_input(client, auth):
    address_id = client.post("/addresses", headers=auth, json=VALID_ADDRESS).get_json()["id"]
    client.post("/cart", headers=auth, json={"product_id": 6, "variant": None})

    assert place(client, auth).status_code == 400                                         # no address
    assert place(client, auth, address_id=address_id, payment_method="bitcoin").status_code == 400
    assert place(client, auth, address_id=address_id, payment_method="card",
                 payment_option="Monopoly Money").status_code == 400
    # Bill is below the first free-gift threshold, so no gifts are allowed.
    assert place(client, auth, address_id=address_id,
                 gifts=[pricing.FREE_GIFTS[0]["name"]]).status_code == 400

    bob = make_user(client, "bob")
    client.post("/cart", headers=bob, json={"product_id": 6, "variant": None})
    assert place(client, bob, address_id=address_id).status_code == 400   # not bob's address
