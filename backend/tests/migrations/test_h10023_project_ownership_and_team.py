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
        / "h10023_add_project_ownership_and_team.py"
    )
    spec = importlib.util.spec_from_file_location("h10023_test_migration", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_h10023_backfills_creator_then_first_administrator_and_is_reversible() -> None:
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
            sa.Column("role", sa.String(32), nullable=False),
            sa.Column("password_hash", sa.String(512), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
        )
        sa.Table(
            "projects",
            metadata,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(255), nullable=False),
        )
        sa.Table(
            "audit_events",
            metadata,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("actor_user_id", sa.Integer(), nullable=True),
            sa.Column("action", sa.String(64), nullable=False),
            sa.Column("entity_type", sa.String(64), nullable=False),
            sa.Column("entity_id", sa.String(255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        metadata.create_all(connection)
        connection.execute(
            sa.text(
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
            sa.text(
                "INSERT INTO projects (id, name) VALUES (10, 'С аудитом'), (20, 'Без аудита')"
            )
        )
        connection.execute(
            sa.text(
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

        columns = {item["name"] for item in sa.inspect(connection).get_columns("projects")}
        assert "owner_user_id" in columns
        owners = connection.execute(
            sa.text("SELECT id, owner_user_id FROM projects ORDER BY id")
        ).all()
        assert owners == [(10, 2), (20, 1)]
        assert "project_instructors" in sa.inspect(connection).get_table_names()

        migration.downgrade()
        columns = {item["name"] for item in sa.inspect(connection).get_columns("projects")}
        assert "owner_user_id" not in columns
        assert "project_instructors" not in sa.inspect(connection).get_table_names()
