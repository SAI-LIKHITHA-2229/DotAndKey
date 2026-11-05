import pytest

from conftest import VALID_ADDRESS

# Bodies that are valid JSON but not the object the API expects.
WRONG_SHAPES = ["[1, 2]", '"just a string"', "42", "null", "not json at all"]


@pytest.mark.parametrize("body", WRONG_SHAPES)
@pytest.mark.parametrize("path", ["/register", "/login"])
def test_public_routes_reject_wrong_body_shape(client, path, body):
    response = client.post(path, data=body, content_type="application/json")
    assert response.status_code in (400, 401)
    assert "error" in response.get_json()


@pytest.mark.parametrize("body", WRONG_SHAPES)
@pytest.mark.parametrize("path", ["/cart", "/addresses", "/orders"])
def test_protected_routes_reject_wrong_body_shape(client, auth, path, body):
    response = client.post(path, headers=auth, data=body, content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_wrong_field_types_are_rejected_not_crashing(client, auth):
    assert client.post("/register", json={"username": 123, "password": "password123"}).status_code == 400
    assert client.post("/register", json={"username": "alice", "password": 12345678}).status_code == 400
    assert client.post("/login", json={"username": ["alice"], "password": {}}).status_code == 401
    assert client.post("/cart", headers=auth, json={"product_id": 1, "variant": 7}).status_code == 400
    assert client.post("/addresses", headers=auth,
                       json={**VALID_ADDRESS, "mobile": 9876543210}).status_code == 400
    assert client.post("/orders", headers=auth,
                       json={"address_id": 1, "payment_method": "card", "payment_option": 5}).status_code == 400
