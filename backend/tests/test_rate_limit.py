import pytest

from api import create_app
from api.extensions import limiter
from conftest import TEST_SECRET


@pytest.fixture
def limited_client():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": TEST_SECRET,
        "RATELIMIT_ENABLED": True,
    })
    with app.app_context():
        limiter.reset()
    with app.test_client() as client:
        yield client


def test_login_is_rate_limited(limited_client):
    body = {"username": "alice", "password": "wrong-password"}
    for _ in range(10):
        assert limited_client.post("/login", json=body).status_code == 401

    response = limited_client.post("/login", json=body)
    assert response.status_code == 429
    assert "Too many attempts" in response.get_json()["error"]


def test_register_is_rate_limited(limited_client):
    for number in range(10):
        response = limited_client.post("/register", json={"username": f"user{number}",
                                                          "password": "password123"})
        assert response.status_code == 201

    response = limited_client.post("/register", json={"username": "one_too_many",
                                                      "password": "password123"})
    assert response.status_code == 429
