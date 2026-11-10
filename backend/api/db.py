import logging
from contextlib import closing

import psycopg
from flask import current_app
from psycopg.rows import dict_row

log = logging.getLogger(__name__)


def get_db_connection():
    """Open a new PostgreSQL connection. The caller must close it."""
    url = current_app.config["DATABASE_URL"]
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    try:
        # dict_row: read columns by name, as in row["id"].
        # connect_timeout: give up after 10 seconds instead of hanging.
        return psycopg.connect(url, row_factory=dict_row, connect_timeout=10)
    except psycopg.ProgrammingError:
        # A malformed address: the driver's message could repeat the password.
        raise RuntimeError("DATABASE_URL is not a valid PostgreSQL address") from None


# ---- Migrations ----
# Each entry upgrades the schema once, and schema_migrations remembers which
# ones have run. Never edit a released entry; add a new one instead.
_INITIAL_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        token_version INTEGER NOT NULL DEFAULT 0
    )
    """,
    # Usernames are unique ignoring case: Alice and alice are the same person.
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_lower ON users (lower(username))",
    """
    CREATE TABLE IF NOT EXISTS cart (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        product_id INTEGER NOT NULL,
        variant TEXT NOT NULL DEFAULT '',
        quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
        UNIQUE (user_id, product_id, variant)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS addresses (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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
    """,
    "CREATE INDEX IF NOT EXISTS idx_addresses_user_id ON addresses (user_id)",
    # RESTRICT: a user who has orders can't be deleted, so history is never lost.
    """
    CREATE TABLE IF NOT EXISTS orders (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
        items TEXT NOT NULL,
        total INTEGER NOT NULL,
        address TEXT,
        payment_method TEXT,
        status TEXT NOT NULL DEFAULT 'confirmed'
            CHECK (status IN ('confirmed', 'shipped', 'delivered', 'cancelled')),
        payment_status TEXT NOT NULL DEFAULT 'pending'
            CHECK (payment_status IN ('pending', 'demo_paid')),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders (user_id)",
)


MIGRATIONS = (
    (1, "initial_schema", _INITIAL_SCHEMA),
)

# Any number works, as long as every copy of the app uses the same one.
MIGRATION_LOCK_ID = 726354


def migrate(conn, up_to=None):
    """Apply the missing migrations in one transaction and commit it.

    `up_to` stops at an earlier version; tests use it to build an old schema.
    """
    # Only one process migrates at a time. The lock ends with the transaction.
    conn.execute("SELECT pg_advisory_xact_lock(%s)", (MIGRATION_LOCK_ID,))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    applied = {row["version"] for row in conn.execute("SELECT version FROM schema_migrations")}

    for version, name, statements in MIGRATIONS:
        if version in applied or (up_to is not None and version > up_to):
            continue
        for statement in statements:
            conn.execute(statement)
        conn.execute("INSERT INTO schema_migrations (version, name) VALUES (%s, %s)",
                     (version, name))
        log.info("Applied database migration %d (%s)", version, name)
    conn.commit()


def init_db():
    with closing(get_db_connection()) as conn:
        migrate(conn)
