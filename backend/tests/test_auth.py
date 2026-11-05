import datetime
import sqlite3

import jwt

from conftest import TEST_SECRET, make_user

CSRF = {"X-Requested-With": "XMLHttpRequest"}


def login(client, username="alice", password="password123"):
    return client.post("/login", json={"username": username, "password": password})


def test_login_sets_an_httponly_session_cookie(client):
    assert client.post("/register", json={"username": "alice", "password": "password123"}).status_code == 201

    response = login(client)
    assert response.status_code == 200
    body = response.get_json()
    assert body["username"] == "alice"
    assert "token" not in body                       # never exposed to page JavaScript

    set_cookie = response.headers["Set-Cookie"]
    assert "dk_session=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=Lax" in set_cookie

    payload = jwt.decode(client.get_cookie("dk_session").value, TEST_SECRET, algorithms=["HS256"])
    assert payload["username"] == "alice"
    assert "exp" in payload


def test_me_reports_the_logged_in_user(client):
    client.post("/register", json={"username": "alice", "password": "password123"})
    assert client.get("/me").status_code == 401

    login(client)
    response = client.get("/me")
    assert response.status_code == 200
    assert response.get_json()["username"] == "alice"
    assert "expires_at" in response.get_json()


def test_cookie_writes_need_the_csrf_header(client):
    client.post("/register", json={"username": "alice", "password": "password123"})
    login(client)
    item = {"product_id": 6, "variant": None}

    assert client.post("/cart", json=item).status_code == 403
    assert client.post("/cart", json=item, headers=CSRF).status_code == 201
    assert client.get("/cart").status_code == 200    # reads don't need it


def test_logout_revokes_the_token_everywhere(client):
    header = make_user(client)                       # a copied token
    assert client.get("/cart", headers=header).status_code == 200

    assert client.post("/logout", headers=header).status_code == 200
    assert client.get("/cart", headers=header).status_code == 401


def test_logout_clears_the_cookie(client):
    client.post("/register", json={"username": "alice", "password": "password123"})
    login(client)
    response = client.post("/logout")
    assert "dk_session=;" in response.headers["Set-Cookie"]
    assert client.get("/me").status_code == 401


def test_tokens_for_deleted_users_are_rejected(app, client):
    header = make_user(client)
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()

    assert client.get("/cart", headers=header).status_code == 401


def test_expired_tokens_are_rejected(client):
    make_user(client)
    past = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)
    token = jwt.encode({"user_id": 1, "username": "alice", "ver": 0, "exp": past},
                       TEST_SECRET, algorithm="HS256")
    response = client.get("/cart", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "expired" in response.get_json()["error"]


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
    wrong_password = login(client, password="nope-nope")
    unknown_user = login(client, username="nobody")

    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.get_json() == unknown_user.get_json()


def test_unknown_user_still_runs_a_password_check(client, monkeypatch):
    """Both failure paths do the same (slow) hash work, so timing reveals nothing."""
    import api.auth

    calls = []
    real_check = api.auth.check_password_hash
    monkeypatch.setattr(api.auth, "check_password_hash",
                        lambda stored, given: calls.append(stored) or real_check(stored, given))

    make_user(client)
    calls.clear()
    login(client, password="wrong-password")
    login(client, username="nobody", password="wrong-password")

    assert len(calls) == 2
    assert calls[1] == api.auth.DUMMY_PASSWORD_HASH


def test_protected_routes_require_a_valid_token(client):
    assert client.get("/cart").status_code == 401
    bad = {"Authorization": "Bearer not-a-real-token"}
    assert client.get("/cart", headers=bad).status_code == 401


def test_errors_are_json(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "error" in response.get_json()
