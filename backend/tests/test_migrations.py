import json
from contextlib import closing

import psycopg
import pytest

from api import create_app
from api.cart import cart_lines
from api.db import MIGRATIONS, get_db_connection, migrate
from conftest import TEST_SECRET, connect_to_test_database, erase_test_schema, run_at_once

LIP_MASK_ID = 6


def add_user():
    with connect_to_test_database() as conn:
        return conn.execute(
            "INSERT INTO users (username, password_hash) VALUES ('alice', 'x') RETURNING id"
        ).fetchone()["id"]


def applied_versions():
    with connect_to_test_database() as conn:
        rows = conn.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()
    return [row["version"] for row in rows]


def test_cart_prices_come_from_catalog_and_unknown_products_are_dropped(app):
    """The cart stores no price, so a saved row can only be charged the catalog price."""
    user_id = add_user()
    with connect_to_test_database() as conn:
        conn.execute(
            "INSERT INTO cart (user_id, product_id, variant, quantity) "
            "VALUES (%s, %s, '', 2), (%s, 99999, '', 1)",
            (user_id, LIP_MASK_ID, user_id),
        )

    with app.app_context(), closing(get_db_connection()) as conn:
        lines = cart_lines(conn, user_id)

    assert [(line["product_name"], line["price"], line["quantity"]) for line in lines] == [
        ("Lip Mask", 399, 2)
    ]


def test_migrations_run_once():
    config = {"TESTING": True, "SECRET_KEY": TEST_SECRET}
    create_app(config)
    add_user()

    create_app(config)   # a second start must not fail or lose data

    with connect_to_test_database() as conn:
        assert conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"] == 1
    assert applied_versions() == [version for version, _, _ in MIGRATIONS]


def test_simultaneous_starts_apply_each_migration_once():
    erase_test_schema()

    def start(_):
        with connect_to_test_database() as conn:
            migrate(conn)

    run_at_once(8, start)

    assert applied_versions() == [version for version, _, _ in MIGRATIONS]


def test_order_items_migration_keeps_existing_orders():
    """An order saved with the old JSON column keeps every item, in order."""
    erase_test_schema()
    with connect_to_test_database() as conn:
        migrate(conn, up_to=1)
    user_id = add_user()
    old_items = [
        {"product_name": "Lip Mask", "price": 399, "quantity": 2, "image": "lip.jpg"},
        {"product_name": "Gift (Free gift)", "price": 0, "quantity": 1, "image": "gift.jpg"},
    ]
    with connect_to_test_database() as conn:
        conn.execute("INSERT INTO orders (user_id, items, total) VALUES (%s, %s, 798)",
                     (user_id, json.dumps(old_items)))

    with connect_to_test_database() as conn:
        migrate(conn)
        rows = conn.execute(
            "SELECT product_name, price, quantity, image FROM order_items ORDER BY id"
        ).fetchall()
        columns = {row["column_name"] for row in conn.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'orders'"
        )}

    assert rows == old_items
    assert "items" not in columns


def test_foreign_keys_are_enforced(app):
    with app.app_context(), closing(get_db_connection()) as conn:
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            conn.execute("INSERT INTO cart (user_id, product_id, variant, quantity) "
                         "VALUES (12345, 6, '', 1)")


@pytest.mark.parametrize("address", [
    "postgresql://user:FAKESECRET%ZZ@localhost:5432/x",   # broken percent-encoding
    "postgresql://user:FAKESECRET@localhost:notaport/x",
])
def test_bad_database_address_is_not_repeated_in_errors(app, address):
    app.config["DATABASE_URL"] = address
    with app.app_context(), pytest.raises(Exception) as caught:
        get_db_connection()
    assert "FAKESECRET" not in str(caught.value)
