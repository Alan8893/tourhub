import importlib.util
from pathlib import Path
from types import ModuleType

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, inspect, text


def _migration_module() -> ModuleType:
    path = (
        Path(__file__).resolve().parents[2]
        / "alembic"
        / "versions"
        / "h10022_add_user_contact_profiles.py"
    )
    spec = importlib.util.spec_from_file_location("h10022_test_migration", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_h10022_adds_nullable_contact_columns_and_is_reversible() -> None:
    engine = create_engine("sqlite:///:memory:")
    migration = _migration_module()

    with engine.begin() as connection:
        metadata = MetaData()
        Table(
            "users",
            metadata,
            Column("id", Integer(), primary_key=True),
            Column("email", String(320), nullable=False),
            Column("display_name", String(120), nullable=False),
        )
        metadata.create_all(connection)
        connection.execute(
            text(
                "INSERT INTO users (id, email, display_name) "
                "VALUES (1, 'member@example.org', 'Участник клуба')"
            )
        )

        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()

        columns = {item["name"]: item for item in inspect(connection).get_columns("users")}
        for column_name in ("phone", "telegram_url", "max_url", "vk_url"):
            assert column_name in columns
            assert columns[column_name]["nullable"] is True
        row = connection.execute(
            text(
                "SELECT phone, telegram_url, max_url, vk_url FROM users WHERE id = 1"
            )
        ).one()
        assert tuple(row) == (None, None, None, None)

        migration.downgrade()
        remaining = {item["name"] for item in inspect(connection).get_columns("users")}
        assert not {"phone", "telegram_url", "max_url", "vk_url"} & remaining
