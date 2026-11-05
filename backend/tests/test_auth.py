import jwt

import app as app_module
from conftest import make_user


def test_register_and_login_returns_token(client):
    response = client.post("/register", json={"username": "alice", "password": "password123"})
    assert response.status_code == 201

    response = client.post("/login", json={"username": "alice", "password": "password123"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["username"] == "alice"

    payload = jwt.decode(body["token"], app_module.SECRET_KEY, algorithms=["HS256"])
    assert payload["username"] == "alice"
    assert "exp" in payload


def test_register_rejects_invalid_username_and_password(client):
    assert client.post("/register", json={"username": "ab", "password": "password123"}).status_code == 400
    assert client.post("/register", json={"username": "bad name!", "password": "password123"}).status_code == 400
    assert client.post("/register", json={"username": "a" * 31, "password": "password123"}).status_code == 400
    assert client.post("/register", json={"username": "alice", "password": "short"}).status_code == 400


def test_usernames_are_unique_ignoring_case(client):
    make_user(client, "Alice")
    response = client.post("/register", json={"username": "alice", "password": "password123"})
    assert response.status_code == 409


def test_login_uses_same_message_for_unknown_user_and_wrong_password(client):
    make_user(client)
    wrong_password = client.post("/login", json={"username": "alice", "password": "nope-nope"})
    unknown_user = client.post("/login", json={"username": "nobody", "password": "password123"})

    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.get_json() == unknown_user.get_json()


def test_protected_routes_require_a_valid_token(client):
    assert client.get("/cart").status_code == 401
    bad = {"Authorization": "Bearer not-a-real-token"}
    assert client.get("/cart", headers=bad).status_code == 401


def test_errors_are_json(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "error" in response.get_json()
