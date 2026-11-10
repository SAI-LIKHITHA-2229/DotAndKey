from contextlib import closing

import psycopg
from flask import current_app
from psycopg.rows import dict_row


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


# Each statement is safe to repeat, so the whole list runs on every start.
SCHEMA = (
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


def create_schema(conn):
    for statement in SCHEMA:
        conn.execute(statement)


def init_db():
    with closing(get_db_connection()) as conn:
        create_schema(conn)
        conn.commit()
