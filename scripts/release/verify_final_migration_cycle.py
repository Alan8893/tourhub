from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
PREVIOUS_REVISION = "h10020"
HEAD_REVISION = "h10021"
DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://tourhub:tourhub@127.0.0.1:5432/tourhub_release_cycle"
)


def _alembic_config() -> Config:
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    return config


def _current_revision(database_url: str) -> str | None:
    engine = sa.create_engine(database_url)
    try:
        with engine.connect() as connection:
            return MigrationContext.configure(connection).get_current_revision()
    finally:
        engine.dispose()


def _assert_revision(database_url: str, expected: str) -> None:
    actual = _current_revision(database_url)
    if actual != expected:
        raise AssertionError(f"Expected Alembic revision {expected}, got {actual}")


def _seed_h10020(database_url: str) -> None:
    engine = sa.create_engine(database_url)
    metadata = sa.MetaData()
    try:
        products = sa.Table("products", metadata, autoload_with=engine)
        recipes = sa.Table("recipes", metadata, autoload_with=engine)
        components = sa.Table("recipe_components", metadata, autoload_with=engine)
        dishes = sa.Table("dishes", metadata, autoload_with=engine)
        variants = sa.Table("dish_recipe_variants", metadata, autoload_with=engine)
        meal_plans = sa.Table("meal_plans", metadata, autoload_with=engine)
        meal_plan_days = sa.Table("meal_plan_days", metadata, autoload_with=engine)
        meal_slots = sa.Table("meal_slots", metadata, autoload_with=engine)
        meal_slot_dishes = sa.Table("meal_slot_dishes", metadata, autoload_with=engine)

        with engine.begin() as connection:
            connection.execute(
                products.insert(),
                [
                    {
                        "id": "product-vodka",
                        "name": "Водка",
                        "category": "Напитки",
                        "unit": "millilitre",
                        "package_size": 500,
                    },
                    {
                        "id": "product-chamomile",
                        "name": "Ромашка",
                        "category": "Травы",
                        "unit": "gram",
                        "package_size": 100,
                    },
                    {
                        "id": "product-vinegar",
                        "name": "Винный уксус",
                        "category": "Приправы",
                        "unit": "millilitre",
                        "package_size": 250,
                    },
                ],
            )
            connection.execute(
                recipes.insert(),
                [
                    {
                        "id": "recipe-prohibited-component",
                        "name": "Походный чай",
                        "scope": "club",
                        "owner_user_id": None,
                        "lifecycle_status": "published",
                        "submitted_by_user_id": None,
                        "submitted_at": None,
                        "reviewed_by_user_id": None,
                        "reviewed_at": None,
                        "review_comment": None,
                        "is_archived": False,
                    },
                    {
                        "id": "recipe-prohibited-name",
                        "name": "Ром с чаем",
                        "scope": "club",
                        "owner_user_id": None,
                        "lifecycle_status": "published",
                        "submitted_by_user_id": None,
                        "submitted_at": None,
                        "reviewed_by_user_id": None,
                        "reviewed_at": None,
                        "review_comment": None,
                        "is_archived": False,
                    },
                    {
                        "id": "recipe-allowed",
                        "name": "Травяной чай",
                        "scope": "club",
                        "owner_user_id": None,
                        "lifecycle_status": "published",
                        "submitted_by_user_id": None,
                        "submitted_at": None,
                        "reviewed_by_user_id": None,
                        "reviewed_at": None,
                        "review_comment": None,
                        "is_archived": False,
                    },
                    {
                        "id": "recipe-manual-archive",
                        "name": "Запасной чай",
                        "scope": "club",
                        "owner_user_id": None,
                        "lifecycle_status": "published",
                        "submitted_by_user_id": None,
                        "submitted_at": None,
                        "reviewed_by_user_id": None,
                        "reviewed_at": None,
                        "review_comment": None,
                        "is_archived": True,
                    },
                ],
            )
            connection.execute(
                components.insert(),
                [
                    {
                        "id": "component-prohibited",
                        "recipe_id": "recipe-prohibited-component",
                        "product_id": "product-vodka",
                        "component_type": "base",
                        "amount": 10,
                        "unit": "millilitre",
                        "calculation_type": "per_person",
                        "people_count": None,
                    },
                    {
                        "id": "component-allowed",
                        "recipe_id": "recipe-allowed",
                        "product_id": "product-chamomile",
                        "component_type": "base",
                        "amount": 5,
                        "unit": "gram",
                        "calculation_type": "per_person",
                        "people_count": None,
                    },
                    {
                        "id": "component-manual",
                        "recipe_id": "recipe-manual-archive",
                        "product_id": "product-chamomile",
                        "component_type": "base",
                        "amount": 5,
                        "unit": "gram",
                        "calculation_type": "per_person",
                        "people_count": None,
                    },
                ],
            )
            connection.execute(
                dishes.insert(),
                [
                    {
                        "id": "dish-prohibited-default",
                        "name": "Вечерний напиток",
                        "recipe_id": "recipe-prohibited-component",
                    },
                    {
                        "id": "dish-prohibited-name",
                        "name": "Пиво к ужину",
                        "recipe_id": "recipe-allowed",
                    },
                    {
                        "id": "dish-allowed",
                        "name": "Травяной чай",
                        "recipe_id": "recipe-allowed",
                    },
                    {
                        "id": "dish-non-default-variant",
                        "name": "Чайный набор",
                        "recipe_id": "recipe-allowed",
                    },
                ],
            )
            connection.execute(
                variants.insert(),
                [
                    {
                        "dish_id": "dish-prohibited-default",
                        "recipe_id": "recipe-prohibited-component",
                        "position": 0,
                    },
                    {
                        "dish_id": "dish-prohibited-name",
                        "recipe_id": "recipe-allowed",
                        "position": 0,
                    },
                    {
                        "dish_id": "dish-allowed",
                        "recipe_id": "recipe-allowed",
                        "position": 0,
                    },
                    {
                        "dish_id": "dish-non-default-variant",
                        "recipe_id": "recipe-allowed",
                        "position": 0,
                    },
                    {
                        "dish_id": "dish-non-default-variant",
                        "recipe_id": "recipe-prohibited-name",
                        "position": 1,
                    },
                ],
            )
            connection.execute(
                meal_plans.insert(),
                {
                    "id": "historical-plan",
                    "project_id": None,
                    "name": "Исторический план",
                    "participants": 4,
                    "days_count": 1,
                    "warnings": [],
                },
            )
            connection.execute(
                meal_plan_days.insert(),
                {
                    "id": "historical-day",
                    "meal_plan_id": "historical-plan",
                    "day_number": 1,
                },
            )
            connection.execute(
                meal_slots.insert(),
                {
                    "id": "historical-slot",
                    "meal_plan_day_id": "historical-day",
                    "meal_type": "dinner",
                    "name": "Исторический ужин",
                    "order": 0,
                    "is_manually_edited": True,
                },
            )
            connection.execute(
                meal_slot_dishes.insert(),
                {
                    "id": "historical-assignment",
                    "meal_slot_id": "historical-slot",
                    "dish_id": "dish-prohibited-default",
                    "recipe_id": "recipe-prohibited-component",
                    "order": 0,
                },
            )
    finally:
        engine.dispose()


def _rows_by_id(engine: sa.Engine, table_name: str) -> dict[str, dict[str, Any]]:
    metadata = sa.MetaData()
    table = sa.Table(table_name, metadata, autoload_with=engine)
    with engine.connect() as connection:
        rows = connection.execute(sa.select(table)).mappings()
        return {str(row["id"]): dict(row) for row in rows}


def _column_names(engine: sa.Engine, table_name: str) -> set[str]:
    return {str(column["name"]) for column in sa.inspect(engine).get_columns(table_name)}


def _historical_assignment(engine: sa.Engine) -> dict[str, Any]:
    statement = sa.text(
        "SELECT msd.id, msd.dish_id, msd.recipe_id, d.name AS dish_name, "
        "r.name AS recipe_name FROM meal_slot_dishes AS msd "
        "JOIN dishes AS d ON d.id = msd.dish_id "
        "JOIN recipes AS r ON r.id = msd.recipe_id "
        "WHERE msd.id = 'historical-assignment'"
    )
    with engine.connect() as connection:
        row = connection.execute(statement).mappings().one()
        return dict(row)


def _verify_h10021(database_url: str) -> dict[str, Any]:
    engine = sa.create_engine(database_url)
    try:
        products = _rows_by_id(engine, "products")
        recipes = _rows_by_id(engine, "recipes")
        dishes = _rows_by_id(engine, "dishes")

        expected_flags = {
            "product-vodka": (True, True),
            "product-chamomile": (False, False),
            "product-vinegar": (False, False),
        }
        for row_id, flags in expected_flags.items():
            actual = (
                bool(products[row_id]["is_archived"]),
                bool(products[row_id]["archived_by_alcohol_policy"]),
            )
            if actual != flags:
                raise AssertionError(f"Unexpected Product flags for {row_id}: {actual}")

        expected_recipe_flags = {
            "recipe-prohibited-component": (True, True),
            "recipe-prohibited-name": (True, True),
            "recipe-allowed": (False, False),
            "recipe-manual-archive": (True, False),
        }
        for row_id, flags in expected_recipe_flags.items():
            actual = (
                bool(recipes[row_id]["is_archived"]),
                bool(recipes[row_id]["archived_by_alcohol_policy"]),
            )
            if actual != flags:
                raise AssertionError(f"Unexpected Recipe flags for {row_id}: {actual}")

        expected_dish_flags = {
            "dish-prohibited-default": (True, True),
            "dish-prohibited-name": (True, True),
            "dish-allowed": (False, False),
            "dish-non-default-variant": (False, False),
        }
        for row_id, flags in expected_dish_flags.items():
            actual = (
                bool(dishes[row_id]["is_archived"]),
                bool(dishes[row_id]["archived_by_alcohol_policy"]),
            )
            if actual != flags:
                raise AssertionError(f"Unexpected Dish flags for {row_id}: {actual}")

        metadata = sa.MetaData()
        product_table = sa.Table("products", metadata, autoload_with=engine)
        recipe_table = sa.Table("recipes", metadata, autoload_with=engine)
        dish_table = sa.Table("dishes", metadata, autoload_with=engine)
        variant_table = sa.Table("dish_recipe_variants", metadata, autoload_with=engine)
        with engine.connect() as connection:
            active_products = set(
                connection.scalars(
                    sa.select(product_table.c.id).where(
                        product_table.c.is_archived.is_(False)
                    )
                )
            )
            active_recipes = set(
                connection.scalars(
                    sa.select(recipe_table.c.id).where(
                        recipe_table.c.is_archived.is_(False)
                    )
                )
            )
            active_dishes = set(
                connection.scalars(
                    sa.select(dish_table.c.id).where(
                        dish_table.c.is_archived.is_(False)
                    )
                )
            )
            non_default_variant = connection.execute(
                sa.select(variant_table).where(
                    variant_table.c.dish_id == "dish-non-default-variant",
                    variant_table.c.recipe_id == "recipe-prohibited-name",
                )
            ).mappings().one()

        if active_products != {"product-chamomile", "product-vinegar"}:
            raise AssertionError(f"Unexpected active Products: {sorted(active_products)}")
        if active_recipes != {"recipe-allowed"}:
            raise AssertionError(f"Unexpected active Recipes: {sorted(active_recipes)}")
        if active_dishes != {"dish-allowed", "dish-non-default-variant"}:
            raise AssertionError(f"Unexpected active Dishes: {sorted(active_dishes)}")

        historical = _historical_assignment(engine)
        if historical["dish_id"] != "dish-prohibited-default":
            raise AssertionError("Historical Dish reference changed")
        if historical["recipe_id"] != "recipe-prohibited-component":
            raise AssertionError("Historical Recipe reference changed")

        return {
            "active_products": sorted(active_products),
            "active_recipes": sorted(active_recipes),
            "active_dishes": sorted(active_dishes),
            "historical_assignment": historical,
            "non_default_variant_position": non_default_variant["position"],
        }
    finally:
        engine.dispose()


def _verify_h10020_after_downgrade(database_url: str) -> dict[str, Any]:
    engine = sa.create_engine(database_url)
    try:
        for table_name in ("products", "dishes"):
            unexpected = {
                "is_archived",
                "archived_by_alcohol_policy",
            } & _column_names(engine, table_name)
            if unexpected:
                raise AssertionError(
                    f"Downgrade kept columns on {table_name}: {unexpected}"
                )
        if "archived_by_alcohol_policy" in _column_names(engine, "recipes"):
            raise AssertionError("Downgrade kept Recipe policy marker")

        recipes = _rows_by_id(engine, "recipes")
        expected_archive_state = {
            "recipe-prohibited-component": False,
            "recipe-prohibited-name": False,
            "recipe-allowed": False,
            "recipe-manual-archive": True,
        }
        for row_id, expected in expected_archive_state.items():
            actual = bool(recipes[row_id]["is_archived"])
            if actual != expected:
                raise AssertionError(
                    f"Unexpected downgraded Recipe archive state for {row_id}: {actual}"
                )

        return {
            "recipe_archive_state": expected_archive_state,
            "historical_assignment": _historical_assignment(engine),
        }
    finally:
        engine.dispose()


def _write_evidence(path: Path, evidence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    database_url = os.environ.get("DATABASE__URL", DEFAULT_DATABASE_URL)
    os.environ["DATABASE__URL"] = database_url
    evidence_path = Path(
        os.environ.get(
            "FINAL_MIGRATION_EVIDENCE_PATH",
            str(ROOT / "final-migration-evidence.json"),
        )
    )
    evidence: dict[str, Any] = {
        "schema_version": 1,
        "status": "running",
        "database": "PostgreSQL 18",
        "cycle": [PREVIOUS_REVISION, HEAD_REVISION, PREVIOUS_REVISION, HEAD_REVISION],
        "commit_sha": os.environ.get("GITHUB_SHA"),
        "steps": [],
    }

    try:
        config = _alembic_config()
        heads = ScriptDirectory.from_config(config).get_heads()
        if heads != [HEAD_REVISION]:
            raise AssertionError(
                f"Expected one Alembic head {HEAD_REVISION}, got {heads}"
            )
        evidence["alembic_heads"] = heads

        command.upgrade(config, PREVIOUS_REVISION)
        _assert_revision(database_url, PREVIOUS_REVISION)
        _seed_h10020(database_url)
        evidence["steps"].append({"revision": PREVIOUS_REVISION, "seeded": True})

        command.upgrade(config, HEAD_REVISION)
        _assert_revision(database_url, HEAD_REVISION)
        first_upgrade = _verify_h10021(database_url)
        evidence["steps"].append(
            {"revision": HEAD_REVISION, "phase": "first_upgrade", **first_upgrade}
        )

        command.downgrade(config, PREVIOUS_REVISION)
        _assert_revision(database_url, PREVIOUS_REVISION)
        downgrade = _verify_h10020_after_downgrade(database_url)
        evidence["steps"].append(
            {"revision": PREVIOUS_REVISION, "phase": "downgrade", **downgrade}
        )

        command.upgrade(config, HEAD_REVISION)
        _assert_revision(database_url, HEAD_REVISION)
        second_upgrade = _verify_h10021(database_url)
        evidence["steps"].append(
            {"revision": HEAD_REVISION, "phase": "second_upgrade", **second_upgrade}
        )

        evidence["status"] = "success"
        evidence["final_revision"] = _current_revision(database_url)
        _write_evidence(evidence_path, evidence)
        print(
            "Final migration cycle passed: "
            f"{PREVIOUS_REVISION} -> {HEAD_REVISION} -> "
            f"{PREVIOUS_REVISION} -> {HEAD_REVISION}."
        )
    except Exception as error:
        evidence["status"] = "failure"
        evidence["error"] = {
            "type": type(error).__name__,
            "message": str(error),
        }
        _write_evidence(evidence_path, evidence)
        raise


if __name__ == "__main__":
    main()
