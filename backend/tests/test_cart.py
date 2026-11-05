from api.cart import MAX_QUANTITY
from api.catalog import PRODUCTS, PRODUCTS_BY_ID
from conftest import make_user

MOISTURIZER_ID = 1
LIP_MASK_ID = 6          # a product without variants
VARIANT = "Watermelon Cooling Gel"


def add(client, auth, product_id=MOISTURIZER_ID, variant=VARIANT, **extra):
    return client.post("/cart", headers=auth,
                       json={"product_id": product_id, "variant": variant, **extra})


def test_products_are_public(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.get_json()) == len(PRODUCTS)


def test_price_comes_from_catalog_not_client(client, auth):
    response = add(client, auth, price=1, product_name="Free stuff", image="x.jpg")
    assert response.status_code == 201

    [item] = client.get("/cart", headers=auth).get_json()
    assert item["product_name"] == f"Moisturizer ({VARIANT})"
    assert item["price"] == PRODUCTS_BY_ID[MOISTURIZER_ID]["price"]
    assert item["image"] == "moisturizer.jpg"


def test_rejects_unknown_product_or_variant(client, auth):
    assert add(client, auth, product_id=9999).status_code == 400
    assert add(client, auth, variant="Not a real variant").status_code == 400
    assert add(client, auth, variant=None).status_code == 400      # variant required
    assert add(client, auth, product_id="1").status_code == 400    # must be an int


def test_product_without_variants(client, auth):
    assert add(client, auth, product_id=LIP_MASK_ID, variant=None).status_code == 201
    assert add(client, auth, product_id=LIP_MASK_ID, variant="Extra").status_code == 400


def test_adding_same_item_twice_increases_quantity(client, auth):
    add(client, auth)
    add(client, auth)
    [item] = client.get("/cart", headers=auth).get_json()
    assert item["quantity"] == 2


def test_quantity_is_capped(client, auth):
    for _ in range(MAX_QUANTITY):
        assert add(client, auth).status_code == 201
    assert add(client, auth).status_code == 400

    [item] = client.get("/cart", headers=auth).get_json()
    assert client.put(f"/cart/{item['id']}/increase", headers=auth).status_code == 400


def test_increase_decrease_and_remove(client, auth):
    add(client, auth)
    [item] = client.get("/cart", headers=auth).get_json()

    assert client.put(f"/cart/{item['id']}/increase", headers=auth).status_code == 200
    assert client.get("/cart", headers=auth).get_json()[0]["quantity"] == 2

    client.put(f"/cart/{item['id']}/decrease", headers=auth)
    client.put(f"/cart/{item['id']}/decrease", headers=auth)   # reaches 0 -> removed
    assert client.get("/cart", headers=auth).get_json() == []

    assert client.put("/cart/9999/increase", headers=auth).status_code == 404
    assert client.put("/cart/9999/decrease", headers=auth).status_code == 404


def test_cart_uses_current_catalog_price(client, auth, monkeypatch):
    add(client, auth, product_id=LIP_MASK_ID, variant=None)
    monkeypatch.setitem(PRODUCTS_BY_ID, LIP_MASK_ID, {**PRODUCTS_BY_ID[LIP_MASK_ID], "price": 450})

    [item] = client.get("/cart", headers=auth).get_json()
    assert item["price"] == 450
    assert client.get("/checkout/summary", headers=auth).get_json()["subtotal"] == 450


def test_discontinued_products_leave_the_cart(client, auth, monkeypatch):
    add(client, auth, product_id=LIP_MASK_ID, variant=None)
    monkeypatch.delitem(PRODUCTS_BY_ID, LIP_MASK_ID)

    assert client.get("/cart", headers=auth).get_json() == []


def test_users_cannot_touch_each_others_cart(client, auth):
    add(client, auth)
    [item] = client.get("/cart", headers=auth).get_json()

    bob = make_user(client, "bob")
    assert client.get("/cart", headers=bob).get_json() == []
    assert client.put(f"/cart/{item['id']}/increase", headers=bob).status_code == 404
    client.delete(f"/cart/{item['id']}", headers=bob)

    assert client.get("/cart", headers=auth).get_json()[0]["quantity"] == 1
