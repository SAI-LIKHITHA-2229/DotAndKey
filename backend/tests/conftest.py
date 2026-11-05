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
    })


@pytest.fixture
def client(app):
    with app.test_client() as test_client:
        yield test_client


def make_user(client, username="alice", password="password123"):
    """Register and log in; return the Authorization header."""
    client.post("/register", json={"username": username, "password": password})
    response = client.post("/login", json={"username": username, "password": password})
    return {"Authorization": f"Bearer {response.get_json()['token']}"}


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
