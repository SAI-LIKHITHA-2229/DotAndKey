import logging
import sqlite3
from contextlib import closing

from flask import current_app

log = logging.getLogger(__name__)


def get_db_connection():
    # timeout / busy_timeout: wait for a lock instead of failing or hanging.
    conn = sqlite3.connect(current_app.config["DATABASE_PATH"], timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    # SQLite only enforces foreign keys when asked to, per connection.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---- Migrations ----
# Each step upgrades the schema by one version. The database remembers its
# version in PRAGMA user_version, so every step runs exactly once.
# Never edit a released step; add a new one instead.

def _v1_initial_schema(conn):
    """The original tables (no-ops on databases that already have them)."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            image TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            items TEXT NOT NULL,
            total INTEGER NOT NULL,
            address TEXT,
            payment_method TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            pincode TEXT NOT NULL,
            flat TEXT NOT NULL,
            area TEXT NOT NULL,
            landmark TEXT,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)

    # Very old databases were created before these cart columns existed.
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(cart)")]
    if "image" not in columns:
        conn.execute("ALTER TABLE cart ADD COLUMN image TEXT")
    if "user_id" not in columns:
        conn.execute("ALTER TABLE cart ADD COLUMN user_id INTEGER")


def _v2_foreign_keys_and_indexes(conn):
    """Tie every row to a real user and index the per-user lookups.

    SQLite cannot add a foreign key to an existing table, so each table is
    rebuilt and its rows copied across. Rows whose user no longer exists
    (e.g. old carts saved before login existed) are dropped.
    """
    conn.execute("""
        CREATE TABLE cart_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_name TEXT NOT NULL,
            price INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
            image TEXT
        )
    """)
    conn.execute("""
        INSERT INTO cart_new (id, user_id, product_name, price, quantity, image)
        SELECT id, user_id, product_name, price, quantity, image FROM cart
        WHERE user_id IN (SELECT id FROM users) AND quantity > 0
    """)

    conn.execute("""
        CREATE TABLE addresses_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            full_name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            pincode TEXT NOT NULL,
            flat TEXT NOT NULL,
            area TEXT NOT NULL,
            landmark TEXT,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)
    conn.execute("""
        INSERT INTO addresses_new SELECT * FROM addresses
        WHERE user_id IN (SELECT id FROM users)
    """)

    conn.execute("""
        CREATE TABLE orders_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            items TEXT NOT NULL,
            total INTEGER NOT NULL,
            address TEXT,
            payment_method TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        INSERT INTO orders_new SELECT * FROM orders
        WHERE user_id IN (SELECT id FROM users)
    """)

    for table in ("cart", "addresses", "orders"):
        conn.execute(f"DROP TABLE {table}")
        conn.execute(f"ALTER TABLE {table}_new RENAME TO {table}")
        conn.execute(f"CREATE INDEX idx_{table}_user_id ON {table}(user_id)")


def _v3_cart_references_catalog(conn):
    """Store what was chosen (product_id + variant), not a copy of its price.

    Prices, names and images are looked up in the catalog whenever the cart
    is read, so a stale or tampered price can never reach checkout. Existing
    rows are matched to the catalog by name; rows that match nothing are dropped.
    """
    from .catalog import PRODUCTS

    names = {}
    for product in PRODUCTS:
        variants = product.get("variants") or []
        if not variants:
            names[product["name"]] = (product["id"], "")
        for variant in variants:
            names[f"{product['name']} ({variant['label']})"] = (product["id"], variant["label"])

    conn.execute("""
        CREATE TABLE cart_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL,
            variant TEXT NOT NULL DEFAULT '',
            quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
            UNIQUE (user_id, product_id, variant)
        )
    """)
    for row in conn.execute("SELECT id, user_id, product_name, quantity FROM cart").fetchall():
        match = names.get(row["product_name"])
        if match is None:
            continue
        conn.execute(
            "INSERT INTO cart_new (id, user_id, product_id, variant, quantity) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT (user_id, product_id, variant) DO UPDATE SET quantity = quantity + excluded.quantity",
            (row["id"], row["user_id"], match[0], match[1], row["quantity"])
        )
    conn.execute("DROP TABLE cart")
    conn.execute("ALTER TABLE cart_new RENAME TO cart")
    conn.execute("CREATE INDEX idx_cart_user_id ON cart(user_id)")


def _v4_token_version(conn):
    """Bumping a user's token_version invalidates every token issued before."""
    conn.execute("ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0")


MIGRATIONS = [
    _v1_initial_schema,
    _v2_foreign_keys_and_indexes,
    _v3_cart_references_catalog,
    _v4_token_version,
]
SCHEMA_VERSION = len(MIGRATIONS)


def migrate(conn):
    version = conn.execute("PRAGMA user_version").fetchone()[0]

    for number, step in enumerate(MIGRATIONS, start=1):
        if number <= version:
            continue

        # Foreign keys must be off while tables are rebuilt; the
        # foreign_key_check below verifies the result before committing.
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN")
        try:
            step(conn)
            problems = conn.execute("PRAGMA foreign_key_check").fetchall()
            if problems:
                raise RuntimeError(f"Migration {number} left broken references: {problems}")
            conn.execute(f"PRAGMA user_version = {number}")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.execute("PRAGMA foreign_keys = ON")
        log.info("Database migrated to version %d", number)


def init_db():
    with closing(get_db_connection()) as conn:
        # WAL lets readers and a writer work concurrently without blocking,
        # which keeps the dev server from wedging under rapid clicks.
        conn.execute("PRAGMA journal_mode = WAL")
        migrate(conn)
