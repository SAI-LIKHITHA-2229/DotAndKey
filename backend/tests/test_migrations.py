import sqlite3

from api import create_app
from api.db import SCHEMA_VERSION
from conftest import TEST_SECRET


def make_legacy_db(path):
    """A database shaped like the app before migrations existed."""
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE cart (id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT NOT NULL,
                           price INTEGER NOT NULL, quantity INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE COLLATE NOCASE, password_hash TEXT NOT NULL);
        CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                             items TEXT NOT NULL, total INTEGER NOT NULL, address TEXT,
                             payment_method TEXT, created_at TEXT NOT NULL);
        CREATE TABLE addresses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                                full_name TEXT NOT NULL, mobile TEXT NOT NULL, pincode TEXT NOT NULL,
                                flat TEXT NOT NULL, area TEXT NOT NULL, landmark TEXT,
                                city TEXT NOT NULL, state TEXT NOT NULL, type TEXT NOT NULL);
        INSERT INTO users (id, username, password_hash) VALUES (1, 'alice', 'x');
        INSERT INTO cart (product_name, price, quantity) VALUES ('Orphan from before login', 399, 1);
        INSERT INTO orders (user_id, items, total, created_at) VALUES (1, '[]', 100, 'now');
        INSERT INTO orders (user_id, items, total, created_at) VALUES (99, '[]', 100, 'now');
    """)
    conn.execute("UPDATE cart SET quantity = 1")
    conn.commit()
    conn.close()


def test_legacy_database_is_upgraded(tmp_path):
    path = tmp_path / "legacy.db"
    make_legacy_db(path)

    create_app({"TESTING": True, "SECRET_KEY": TEST_SECRET, "DATABASE_PATH": str(path)})

    conn = sqlite3.connect(path)
    assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    # Rows without a real owner are gone; Alice's order is kept.
    assert conn.execute("SELECT COUNT(*) FROM cart").fetchone()[0] == 0
    assert conn.execute("SELECT user_id FROM orders").fetchall() == [(1,)]
    # Foreign keys and indexes now exist.
    for table in ("cart", "addresses", "orders"):
        assert conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()
    indexes = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
    assert {"idx_cart_user_id", "idx_addresses_user_id", "idx_orders_user_id"} <= indexes


def test_tampered_legacy_cart_rows_are_repriced(tmp_path):
    """A cart row saved with a client-chosen price is charged the catalog price."""
    path = tmp_path / "legacy.db"
    make_legacy_db(path)
    conn = sqlite3.connect(path)
    conn.execute("ALTER TABLE cart ADD COLUMN image TEXT")
    conn.execute("ALTER TABLE cart ADD COLUMN user_id INTEGER")
    conn.executemany(
        "INSERT INTO cart (product_name, price, quantity, user_id) VALUES (?, ?, ?, 1)",
        [("Lip Mask", 1, 2),                  # real product, fake price
         ("Something we never sold", 5, 1)],  # unknown -> dropped
    )
    conn.commit()
    conn.close()

    app = create_app({"TESTING": True, "SECRET_KEY": TEST_SECRET, "DATABASE_PATH": str(path)})

    from api.cart import cart_lines
    from api.db import get_db_connection
    with app.app_context():
        lines = cart_lines(get_db_connection(), 1)
    assert [(line["product_name"], line["price"], line["quantity"]) for line in lines] == [
        ("Lip Mask", 399, 2)
    ]


def test_migrations_run_once(tmp_path):
    config = {"TESTING": True, "SECRET_KEY": TEST_SECRET, "DATABASE_PATH": str(tmp_path / "x.db")}
    create_app(config)
    create_app(config)   # second start must not fail or re-run steps

    conn = sqlite3.connect(tmp_path / "x.db")
    assert conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION


def test_foreign_keys_are_enforced(app):
    from api.db import get_db_connection

    with app.app_context():
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO cart (user_id, product_id, variant, quantity) "
                         "VALUES (12345, 6, '', 1)")
            raise AssertionError("insert for a missing user should fail")
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
