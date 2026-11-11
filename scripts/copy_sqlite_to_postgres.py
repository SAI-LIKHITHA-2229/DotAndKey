"""One-time copy of backend/cart.db into the PostgreSQL database dotandkey.

Run it once from the project root:
    backend\\.venv\\Scripts\\python.exe scripts\\copy_sqlite_to_postgres.py

It only reads cart.db. It refuses any database other than dotandkey, refuses
to run if data is already there, and saves everything or nothing.
"""
import json
import os
import sqlite3
import sys
from contextlib import closing
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from api.db import migrate, sync_inventory  # noqa: E402

DESTINATION_DATABASE = "dotandkey"

# Parents come first, so every row's owner already exists when it is copied.
COLUMNS = {
    "users": ("id", "username", "password_hash", "token_version"),
    "addresses": ("id", "user_id", "full_name", "mobile", "pincode", "flat", "area",
                  "landmark", "city", "state", "type"),
    "cart": ("id", "user_id", "product_id", "variant", "quantity"),
    "orders": ("id", "user_id", "total", "address", "payment_method", "status",
               "payment_status", "created_at"),
}
DATA_TABLES = (*COLUMNS, "order_items")


def require_destination(url):
    if urlsplit(url).path != f"/{DESTINATION_DATABASE}":
        raise RuntimeError(f"This script only copies into {DESTINATION_DATABASE}")


def read_source(path):
    """Every row of cart.db as dictionaries, opened read-only."""
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as source:
        source.row_factory = sqlite3.Row
        return {
            table: [dict(row) for row in source.execute(f"SELECT * FROM {table} ORDER BY id")]
            for table in COLUMNS
        }


def count_rows(conn, table):
    return conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]


def copy_table(cursor, table, rows):
    names = COLUMNS[table]
    # OVERRIDING SYSTEM VALUE keeps the old ids, so rows still point at each other.
    cursor.executemany(
        f"INSERT INTO {table} ({', '.join(names)}) OVERRIDING SYSTEM VALUE "
        f"VALUES ({', '.join(['%s'] * len(names))})",
        [tuple(row[name] for name in names) for row in rows],
    )


def copy_data(data, conn):
    """Copy `data` into `conn` in one transaction and return the row counts."""
    migrate(conn)
    sync_inventory(conn)

    if any(count_rows(conn, table) for table in DATA_TABLES):
        raise RuntimeError("The destination already has data, so nothing was copied")

    orders = [{**order, "created_at": datetime.fromisoformat(order["created_at"])}
              for order in data["orders"]]
    items = [
        (order["id"], item["product_name"], item["price"], item["quantity"], item["image"])
        for order in data["orders"]
        for item in json.loads(order["items"])
    ]

    with conn.cursor() as cursor:
        for table in COLUMNS:
            copy_table(cursor, table, orders if table == "orders" else data[table])
        cursor.executemany(
            "INSERT INTO order_items (order_id, product_name, price, quantity, image) "
            "VALUES (%s, %s, %s, %s, %s)",
            items,
        )

    # Continue numbering after the highest copied id, so new rows can't clash.
    for table in COLUMNS:
        conn.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                     f"(SELECT MAX(id) FROM {table}))")

    expected = {table: len(data[table]) for table in COLUMNS}
    expected["order_items"] = len(items)
    copied = {table: count_rows(conn, table) for table in DATA_TABLES}
    total_paid = conn.execute("SELECT COALESCE(SUM(total), 0) AS n FROM orders").fetchone()["n"]
    if copied != expected or total_paid != sum(order["total"] for order in data["orders"]):
        conn.rollback()
        raise RuntimeError("The copied rows did not match the source, so nothing was saved")

    conn.commit()
    return copied


def main():
    load_dotenv(BACKEND_DIR / ".env")
    url = os.environ.get("DATABASE_URL", "")
    try:
        require_destination(url)
        data = read_source(BACKEND_DIR / "cart.db")
        with closing(psycopg.connect(url, row_factory=dict_row, connect_timeout=10)) as conn:
            copied = copy_data(data, conn)
    except Exception as error:
        # Only the error's type and first line, with the address blanked out.
        lines = str(error).strip().splitlines()
        message = lines[0].replace(url, "***") if lines and url else ""
        print(f"Copy failed, no data rows were saved. {type(error).__name__}: {message}")
        return 1

    for table, count in copied.items():
        print(f"{table}: {count} rows")
    print("Row counts match the source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
