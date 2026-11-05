import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import create_app  # noqa: E402

TEST_SECRET = "test-secret-key-that-is-at-least-32-bytes"


@pytest.fixture
def app(tmp_path):
    """A fresh app backed by an empty temporary database for every test."""
    return create_app({
        "TESTING": True,
        "SECRET_KEY": TEST_SECRET,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        # Most tests log in many times; the rate-limit test turns it back on.
        "RATELIMIT_ENABLED": False,
    })


@pytest.fixture
def client(app):
    with app.test_client() as test_client:
        yield test_client


def make_user(client, username="alice", password="password123"):
    """Register and log in; return a Bearer header for that user.

    Login sets an httpOnly session cookie. Tests that juggle several users
    copy the token into a header and drop the cookie, so each request says
    exactly who is making it.
    """
    client.post("/register", json={"username": username, "password": password})
    client.post("/login", json={"username": username, "password": password})
    token = client.get_cookie("dk_session").value
    client.delete_cookie("dk_session")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth(client):
    return make_user(client)


VALID_ADDRESS = {
    "full_name": "Alice Example",
    "mobile": "9876543210",
    "pincode": "500001",
    "flat": "12A",
    "area": "MG Road",
    "landmark": "",
    "city": "Hyderabad",
    "state": "Telangana",
    "type": "Home",
}
