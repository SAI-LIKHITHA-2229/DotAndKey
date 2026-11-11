import importlib.util
import json
import os
from contextlib import closing

import pytest

from conftest import BACKEND_DIR, connect_to_test_database

SCRIPT = os.path.join(os.path.dirname(BACKEND_DIR), "scripts", "copy_sqlite_to_postgres.py")
spec = importlib.util.spec_from_file_location("copy_sqlite_to_postgres", SCRIPT)
copy_script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(copy_script)

ITEMS = [
    {"product_name": "Lip Mask", "price": 399, "quantity": 2, "image": "lip.jpg"},
    {"product_name": "Gift (Free gift)", "price": 0, "quantity": 1, "image": "gift.jpg"},
]


def source_data():
    """Rows shaped like cart.db, with gaps in the ids as real data has."""
    return {
        "users": [{"id": 3, "username": "alice", "password_hash": "x", "token_version": 2}],
        "addresses": [{"id": 5, "user_id": 3, "full_name": "Alice", "mobile": "9876543210",
                       "pincode": "500001", "flat": "1", "area": "Road", "landmark": "",
                       "city": "Hyderabad", "state": "Telangana", "type": "Home"}],
        "cart": [{"id": 197, "user_id": 3, "product_id": 6, "variant": "", "quantity": 1}],
        "orders": [{"id": 10, "user_id": 3, "items": json.dumps(ITEMS), "total": 798,
                    "address": "Somewhere", "payment_method": "Cash", "status": "confirmed",
                    "payment_status": "pending",
                    "created_at": "2026-01-02T03:04:05.000006+00:00"}],
    }


def copy(data):
    with closing(connect_to_test_database()) as conn:
        return copy_script.copy_data(data, conn)


def test_guard_only_accepts_the_real_destination():
    copy_script.require_destination("postgresql://u:p@localhost:5432/dotandkey")
    with pytest.raises(RuntimeError):
        copy_script.require_destination("postgresql://u:p@localhost:5432/dotandkey_test")


def test_copy_keeps_ids_items_and_dates():
    assert copy(source_data()) == {"users": 1, "addresses": 1, "cart": 1, "orders": 1,
                                   "order_items": 2}

    with connect_to_test_database() as conn:
        order = conn.execute("SELECT id, user_id, created_at FROM orders").fetchone()
        items = conn.execute("SELECT order_id, product_name, price, quantity, image "
                             "FROM order_items ORDER BY id").fetchall()
        version = conn.execute("SELECT token_version AS v FROM users").fetchone()["v"]

    assert (order["id"], order["user_id"]) == (10, 3)
    assert order["created_at"].isoformat().startswith("2026-01-02")
    assert version == 2
    assert [item.pop("order_id") for item in items] == [10, 10]
    assert items == ITEMS


def test_new_rows_continue_after_the_copied_ids():
    copy(source_data())

    with connect_to_test_database() as conn:
        user = conn.execute("INSERT INTO users (username, password_hash) "
                            "VALUES ('bob', 'x') RETURNING id").fetchone()["id"]
        order = conn.execute("INSERT INTO orders (user_id, total) VALUES (3, 1) "
                             "RETURNING id").fetchone()["id"]

    assert (user, order) == (4, 11)


def test_copy_refuses_a_destination_that_has_data():
    copy(source_data())
    with pytest.raises(RuntimeError, match="already has data"):
        copy(source_data())


def test_a_bad_row_saves_nothing():
    data = source_data()
    data["orders"][0]["status"] = "made_up"       # refused by the table, after other rows

    with pytest.raises(Exception):
        copy(data)

    with connect_to_test_database() as conn:
        for table in copy_script.DATA_TABLES:
            assert conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"] == 0
