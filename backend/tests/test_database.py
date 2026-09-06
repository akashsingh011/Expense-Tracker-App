from sqlalchemy import inspect

from app.core.database import engine
from app.main import app


def test_database_tables_exist():
    inspector = inspect(engine)

    tables = set(inspector.get_table_names())

    assert "users" in tables
    assert "expenses" in tables
    assert "funds" in tables