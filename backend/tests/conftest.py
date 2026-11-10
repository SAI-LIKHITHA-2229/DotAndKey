import os
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

import psycopg
import pytest
from dotenv import load_dotenv
from psycopg.rows import dict_row

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from api import create_app  # noqa: E402
from api.db import migrate  # noqa: E402

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


def connect_to_test_database():
    return psycopg.connect(TEST_URL, row_factory=dict_row, connect_timeout=10)


def erase_test_schema():
    """Remove every table from the test database."""
    require_test_database(TEST_URL)
    with connect_to_test_database() as conn:
        conn.execute("DROP SCHEMA public CASCADE")
        conn.execute("CREATE SCHEMA public")


def rebuild_test_schema():
    """Erase the test database and create the latest tables again."""
    erase_test_schema()
    with connect_to_test_database() as conn:
        migrate(conn)


def run_at_once(count, task):
    """Call task(0) ... task(count - 1) at the same moment; return their results."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(task, range(count)))


def requests_at_once(app, count, request):
    """Run request(client) `count` times at once; return the status codes."""
    def one_request(_):
        with app.test_client() as client:
            return request(client).status_code

    return run_at_once(count, one_request)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """Create the test database if needed and start from fresh tables."""
    admin_url = with_database(TEST_URL, "postgres")
    # CREATE DATABASE cannot run inside a transaction, so autocommit is on.
    with psycopg.connect(admin_url, autocommit=True, connect_timeout=10) as conn:
        found = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DATABASE_NAME,)
        ).fetchone()
        if found is None:
            conn.execute(f"CREATE DATABASE {TEST_DATABASE_NAME}")
    rebuild_test_schema()


@pytest.fixture(autouse=True)
def clean_database(prepare_test_database):
    """Every test starts with empty tables and ids counting from 1."""
    require_test_database(TEST_URL)
    with connect_to_test_database() as conn:
        # Fail clearly instead of waiting forever if a connection was left open.
        conn.execute("SET lock_timeout = '5s'")
        conn.execute("TRUNCATE users, cart, addresses, orders RESTART IDENTITY CASCADE")


@pytest.fixture
def app():
    """A fresh app for every test, using the emptied test database."""
    return create_app({
        "TESTING": True,
        "SECRET_KEY": TEST_SECRET,
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
