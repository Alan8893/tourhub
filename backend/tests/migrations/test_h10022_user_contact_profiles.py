import importlib.util
from pathlib import Path
from types import ModuleType

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


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
    engine = sa.create_engine("sqlite:///:memory:")
    migration = _migration_module()

    with engine.begin() as connection:
        metadata = sa.MetaData()
        sa.Table(
            "users",
            metadata,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(320), nullable=False),
            sa.Column("display_name", sa.String(120), nullable=False),
        )
        metadata.create_all(connection)
        connection.execute(
            sa.text(
                "INSERT INTO users (id, email, display_name) "
                "VALUES (1, 'member@example.org', 'Участник клуба')"
            )
        )

        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()

        columns = {item["name"]: item for item in sa.inspect(connection).get_columns("users")}
        for column_name in ("phone", "telegram_url", "max_url", "vk_url"):
            assert column_name in columns
            assert columns[column_name]["nullable"] is True
        row = connection.execute(
            sa.text(
                "SELECT phone, telegram_url, max_url, vk_url FROM users WHERE id = 1"
            )
        ).one()
        assert tuple(row) == (None, None, None, None)

        migration.downgrade()
        remaining = {item["name"] for item in sa.inspect(connection).get_columns("users")}
        assert not {"phone", "telegram_url", "max_url", "vk_url"} & remaining
