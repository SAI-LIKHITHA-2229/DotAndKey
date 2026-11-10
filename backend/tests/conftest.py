import os
import sys
from urllib.parse import urlsplit

import psycopg
import pytest
from dotenv import load_dotenv

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from api import create_app  # noqa: E402

TEST_SECRET = "test-secret-key-that-is-at-least-32-bytes"
TEST_DATABASE_NAME = "dotandkey_test"


def require_test_database(url):
    """Stop unless `url` is the test database, because tests erase data."""
    if urlsplit(url).path != f"/{TEST_DATABASE_NAME}":
        raise RuntimeError(f"Tests may only use the {TEST_DATABASE_NAME} database")


def with_database(url, name):
    """The same connection address, pointing at a different database."""
    return urlsplit(url)._replace(path=f"/{name}").geturl()


def find_test_url():
    load_dotenv(os.path.join(BACKEND_DIR, ".env"))
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        return explicit
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Set DATABASE_URL in backend/.env or TEST_DATABASE_URL to run the tests")
    return with_database(url, TEST_DATABASE_NAME)


# Runs before any test. Every app built during the tests reads this variable,
# so no test can reach the real database by accident.
TEST_URL = find_test_url()
require_test_database(TEST_URL)
os.environ["DATABASE_URL"] = TEST_URL


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """Create the test database the first time the tests run."""
    admin_url = with_database(TEST_URL, "postgres")
    # CREATE DATABASE cannot run inside a transaction, so autocommit is on.
    with psycopg.connect(admin_url, autocommit=True, connect_timeout=10) as conn:
        found = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DATABASE_NAME,)
        ).fetchone()
        if found is None:
            conn.execute(f"CREATE DATABASE {TEST_DATABASE_NAME}")


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
