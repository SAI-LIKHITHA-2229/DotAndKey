import sqlite3
from contextlib import closing

from flask import current_app


def get_db_connection():
    # timeout / busy_timeout: wait for a lock instead of failing or hanging.
    conn = sqlite3.connect(current_app.config["DATABASE_PATH"], timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db():
    with closing(get_db_connection()) as conn:
        # WAL lets readers and a writer work concurrently without blocking,
        # which keeps the dev server from wedging under rapid clicks.
        conn.execute("PRAGMA journal_mode = WAL")
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

        # Migrate older databases created before these columns existed.
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(cart)")]
        if "image" not in columns:
            conn.execute("ALTER TABLE cart ADD COLUMN image TEXT")
        if "user_id" not in columns:
            conn.execute("ALTER TABLE cart ADD COLUMN user_id INTEGER")

        conn.commit()
