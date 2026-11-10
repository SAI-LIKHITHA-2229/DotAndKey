import psycopg
import pytest

from api import create_app
from api.catalog import PRODUCTS
from api.db import INITIAL_STOCK
from conftest import TEST_SECRET, connect_to_test_database, rebuild_test_schema


def add_user(conn, username="alice"):
    return conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, 'x') RETURNING id", (username,)
    ).fetchone()["id"]


def add_order(conn, user_id, status="confirmed", payment_status="pending"):
    conn.execute(
        "INSERT INTO orders (user_id, total, status, payment_status) "
        "VALUES (%s, 100, %s, %s)",
        (user_id, status, payment_status),
    )


def test_fresh_database_gets_full_schema():
    rebuild_test_schema()

    with connect_to_test_database() as conn:
        tables = {row["table_name"] for row in conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )}
        delete_rules = {row["name"]: row["rule"] for row in conn.execute(
            "SELECT conrelid::regclass::text AS name, confdeltype::text AS rule "
            "FROM pg_constraint WHERE contype = 'f'"
        )}
        indexes = {row["indexname"] for row in conn.execute(
            "SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"
        )}

    assert tables == {"schema_migrations", "users", "cart", "addresses", "orders", "order_items",
                      "inventory"}
    # c = cascade (removed with the user), r = restrict (blocks deleting the user).
    assert delete_rules == {"cart": "c", "addresses": "c", "orders": "r", "order_items": "c"}
    assert {"idx_users_username_lower", "idx_addresses_user_id", "idx_orders_user_id",
            "idx_order_items_order_id"} <= indexes


def test_a_user_with_orders_cannot_be_deleted():
    with connect_to_test_database() as conn:
        add_order(conn, add_user(conn))
        with pytest.raises(psycopg.IntegrityError):
            conn.execute("DELETE FROM users")
        conn.rollback()


@pytest.mark.parametrize("field", ["status", "payment_status"])
def test_order_statuses_must_be_known_values(field):
    with connect_to_test_database() as conn:
        user_id = add_user(conn)
        with pytest.raises(psycopg.errors.CheckViolation):
            add_order(conn, user_id, **{field: "made_up"})
        conn.rollback()


def test_every_catalog_item_starts_with_full_stock():
    expected = sum(len(product.get("variants") or [None]) for product in PRODUCTS)
    with connect_to_test_database() as conn:
        quantities = [row["quantity"] for row in conn.execute("SELECT quantity FROM inventory")]
    assert quantities == [INITIAL_STOCK] * expected


def test_a_restart_does_not_reset_stock():
    with connect_to_test_database() as conn:
        conn.execute("UPDATE inventory SET quantity = 7")
    create_app({"TESTING": True, "SECRET_KEY": TEST_SECRET})
    with connect_to_test_database() as conn:
        assert {row["quantity"] for row in conn.execute("SELECT quantity FROM inventory")} == {7}


def test_stock_cannot_go_below_zero():
    with connect_to_test_database() as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute("UPDATE inventory SET quantity = -1")
        conn.rollback()


def test_usernames_are_unique_in_the_database_ignoring_case():
    with connect_to_test_database() as conn:
        add_user(conn, "Alice")
        with pytest.raises(psycopg.errors.UniqueViolation):
            add_user(conn, "alice")
        conn.rollback()
