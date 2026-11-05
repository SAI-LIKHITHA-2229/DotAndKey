from api import create_app
from conftest import TEST_SECRET


def test_security_headers_on_every_response(client):
    for response in (client.get("/health"), client.get("/does-not-exist")):
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
        assert "Strict-Transport-Security" not in response.headers   # dev only


def test_user_data_is_not_cached(client, auth):
    assert client.get("/cart", headers=auth).headers["Cache-Control"] == "no-store"
    assert "Cache-Control" not in client.get("/products").headers


def test_production_adds_hsts_and_secure_cookies(tmp_path):
    app = create_app({"APP_ENV": "production", "SECRET_KEY": TEST_SECRET,
                      "DATABASE_PATH": str(tmp_path / "prod.db"),
                      "SESSION_COOKIE_SECURE": True, "RATELIMIT_ENABLED": False})
    client = app.test_client()
    assert "max-age=" in client.get("/health").headers["Strict-Transport-Security"]

    client.post("/register", json={"username": "alice", "password": "password123"})
    response = client.post("/login", json={"username": "alice", "password": "password123"})
    assert "Secure" in response.headers["Set-Cookie"]
