import pytest

from api.config import load_config
from conftest import require_test_database


def test_guard_refuses_the_real_database():
    with pytest.raises(RuntimeError):
        require_test_database("postgresql://user:pw@localhost:5432/dotandkey")


def test_guard_accepts_the_test_database():
    require_test_database("postgresql://user:pw@localhost:5432/dotandkey_test")


def test_app_config_points_at_the_test_database():
    require_test_database(load_config()["DATABASE_URL"])
