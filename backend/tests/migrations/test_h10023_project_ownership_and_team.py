import importlib.util
from pathlib import Path
from types import ModuleType

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    inspect,
    text,
)


def _migration_module() -> ModuleType:
    path = (
        Path(__file__).resolve().parents[2]
        / "alembic"
        / "versions"
        / "h10023_add_project_ownership_and_team.py"
    )
    spec = importlib.util.spec_from_file_location("h10023_test_migration", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_h10023_backfills_creator_then_first_administrator_and_is_reversible() -> None:
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
            Column("role", String(32), nullable=False),
            Column("password_hash", String(512), nullable=False),
            Column("is_active", Boolean(), nullable=False),
        )
        Table(
            "projects",
            metadata,
            Column("id", Integer(), primary_key=True),
            Column("name", String(255), nullable=False),
        )
        Table(
            "audit_events",
            metadata,
            Column("id", Integer(), primary_key=True),
            Column("actor_user_id", Integer(), nullable=True),
            Column("action", String(64), nullable=False),
            Column("entity_type", String(64), nullable=False),
            Column("entity_id", String(255), nullable=True),
            Column("created_at", DateTime(), nullable=False),
        )
        metadata.create_all(connection)
        connection.execute(
            text(
                """
                INSERT INTO users
                    (id, email, display_name, role, password_hash, is_active)
                VALUES
                    (1, 'admin@example.org', 'Администратор', 'administrator', 'x', 1),
                    (2, 'owner@example.org', 'Создатель', 'instructor', 'x', 0)
                """
            )
        )
        connection.execute(
            text(
                "INSERT INTO projects (id, name) VALUES (10, 'С аудитом'), (20, 'Без аудита')"
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO audit_events
                    (id, actor_user_id, action, entity_type, entity_id, created_at)
                VALUES
                    (1, 2, 'project_created', 'project', '10', '2026-01-01 10:00:00')
                """
            )
        )

        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()

        columns = {item["name"] for item in inspect(connection).get_columns("projects")}
        assert "owner_user_id" in columns
        owners = connection.execute(
            text("SELECT id, owner_user_id FROM projects ORDER BY id")
        ).all()
        assert owners == [(10, 2), (20, 1)]
        assert "project_instructors" in inspect(connection).get_table_names()

        migration.downgrade()
        columns = {item["name"] for item in inspect(connection).get_columns("projects")}
        assert "owner_user_id" not in columns
        assert "project_instructors" not in inspect(connection).get_table_names()
