import os
import sys
import tempfile

import pytest

# Point the app at a throwaway database *before* it is imported,
# so the import-time init_db() never touches the real cart.db.
os.environ["DATABASE_PATH"] = os.path.join(tempfile.mkdtemp(), "import.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-bytes")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A test client backed by a fresh, empty database for every test."""
    monkeypatch.setattr(app_module, "DATABASE_PATH", str(tmp_path / "test.db"))
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
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
