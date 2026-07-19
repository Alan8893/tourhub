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
        / "h10021_enforce_alcohol_prohibition.py"
    )
    spec = importlib.util.spec_from_file_location("h10021_test_migration", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_h10020_shape(connection: sa.Connection) -> None:
    metadata = sa.MetaData()
    sa.Table(
        "products",
        metadata,
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
    )
    sa.Table(
        "recipes",
        metadata,
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "is_archived",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    sa.Table(
        "recipe_components",
        metadata,
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("recipe_id", sa.String(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
    )
    sa.Table(
        "dishes",
        metadata,
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("recipe_id", sa.String(), nullable=False),
    )
    metadata.create_all(connection)


def test_h10021_archives_existing_prohibited_records_and_is_reversible() -> None:
    engine = sa.create_engine("sqlite:///:memory:")
    migration = _migration_module()

    with engine.begin() as connection:
        _create_h10020_shape(connection)
        connection.execute(
            sa.text(
                "INSERT INTO products (id, name, category) VALUES "
                "('vodka', 'Водка', 'Напитки'), "
                "('chamomile', 'Ромашка', 'Травы')"
            )
        )
        connection.execute(
            sa.text(
                "INSERT INTO recipes (id, name, is_archived) VALUES "
                "('bad-recipe', 'Походный чай', false), "
                "('good-recipe', 'Травяной чай', false)"
            )
        )
        connection.execute(
            sa.text(
                "INSERT INTO recipe_components (id, recipe_id, product_id) VALUES "
                "('bad-component', 'bad-recipe', 'vodka'), "
                "('good-component', 'good-recipe', 'chamomile')"
            )
        )
        connection.execute(
            sa.text(
                "INSERT INTO dishes (id, name, recipe_id) VALUES "
                "('bad-default', 'Вечерний напиток', 'bad-recipe'), "
                "('bad-name', 'Пиво к ужину', 'good-recipe'), "
                "('good-dish', 'Травяной чай', 'good-recipe')"
            )
        )

        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()

        products = {
            row.id: row
            for row in connection.execute(
                sa.text(
                    "SELECT id, is_archived, archived_by_alcohol_policy FROM products"
                )
            ).mappings()
        }
        recipes = {
            row.id: row
            for row in connection.execute(
                sa.text(
                    "SELECT id, is_archived, archived_by_alcohol_policy FROM recipes"
                )
            ).mappings()
        }
        dishes = {
            row.id: row
            for row in connection.execute(
                sa.text(
                    "SELECT id, is_archived, archived_by_alcohol_policy FROM dishes"
                )
            ).mappings()
        }

        assert products["vodka"].is_archived == 1
        assert products["vodka"].archived_by_alcohol_policy == 1
        assert products["chamomile"].is_archived == 0
        assert recipes["bad-recipe"].is_archived == 1
        assert recipes["bad-recipe"].archived_by_alcohol_policy == 1
        assert recipes["good-recipe"].is_archived == 0
        assert dishes["bad-default"].is_archived == 1
        assert dishes["bad-name"].is_archived == 1
        assert dishes["good-dish"].is_archived == 0

        migration.downgrade()
        assert "archived_by_alcohol_policy" not in {
            column["name"] for column in sa.inspect(connection).get_columns("recipes")
        }
        assert connection.scalar(
            sa.text("SELECT is_archived FROM recipes WHERE id = 'bad-recipe'")
        ) == 0
