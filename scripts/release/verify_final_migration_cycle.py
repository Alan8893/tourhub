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

SEED_STATEMENTS = (
    """
    INSERT INTO products (id, name, category, unit, package_size) VALUES
      ('product-vodka', 'Водка', 'Напитки', 'millilitre', 500),
      ('product-chamomile', 'Ромашка', 'Травы', 'gram', 100),
      ('product-vinegar', 'Винный уксус', 'Приправы', 'millilitre', 250)
    """,
    """
    INSERT INTO recipes (
      id, name, scope, owner_user_id, lifecycle_status,
      submitted_by_user_id, submitted_at, reviewed_by_user_id,
      reviewed_at, review_comment, is_archived
    ) VALUES
      ('recipe-prohibited-component', 'Походный чай', 'club', NULL, 'published',
       NULL, NULL, NULL, NULL, NULL, false),
      ('recipe-prohibited-name', 'Ром с чаем', 'club', NULL, 'published',
       NULL, NULL, NULL, NULL, NULL, false),
      ('recipe-allowed', 'Травяной чай', 'club', NULL, 'published',
       NULL, NULL, NULL, NULL, NULL, false),
      ('recipe-manual-archive', 'Запасной чай', 'club', NULL, 'published',
       NULL, NULL, NULL, NULL, NULL, true)
    """,
    """
    INSERT INTO recipe_components (
      id, recipe_id, product_id, component_type, amount,
      unit, calculation_type, people_count
    ) VALUES
      ('component-prohibited', 'recipe-prohibited-component', 'product-vodka',
       'base', 10, 'millilitre', 'per_person', NULL),
      ('component-allowed', 'recipe-allowed', 'product-chamomile',
       'base', 5, 'gram', 'per_person', NULL),
      ('component-manual', 'recipe-manual-archive', 'product-chamomile',
       'base', 5, 'gram', 'per_person', NULL)
    """,
    """
    INSERT INTO dishes (id, name, recipe_id) VALUES
      ('dish-prohibited-default', 'Вечерний напиток', 'recipe-prohibited-component'),
      ('dish-prohibited-name', 'Пиво к ужину', 'recipe-allowed'),
      ('dish-allowed', 'Травяной чай', 'recipe-allowed'),
      ('dish-non-default-variant', 'Чайный набор', 'recipe-allowed')
    """,
    """
    INSERT INTO dish_recipe_variants (dish_id, recipe_id, position) VALUES
      ('dish-prohibited-default', 'recipe-prohibited-component', 0),
      ('dish-prohibited-name', 'recipe-allowed', 0),
      ('dish-allowed', 'recipe-allowed', 0),
      ('dish-non-default-variant', 'recipe-allowed', 0),
      ('dish-non-default-variant', 'recipe-prohibited-name', 1)
    """,
    """
    INSERT INTO projects (
      id, name, participants, days, start_date, first_meal,
      last_meal, recipe_generation_mode, status
    ) VALUES
      (1, 'Исторический проект', 4, 1, NULL, 'dinner',
       'dinner', 'club_only', 'draft')
    """,
    """
    INSERT INTO meal_plans (
      id, name, participants, days_count, project_id, warnings
    ) VALUES
      ('historical-plan', 'Исторический план', 4, 1, 1, '[]'::json)
    """,
    """
    INSERT INTO meal_plan_days (id, meal_plan_id, day_number) VALUES
      ('historical-day', 'historical-plan', 1)
    """,
    """
    INSERT INTO meal_slots (
      id, meal_plan_day_id, meal_type, name, "order", is_manually_edited
    ) VALUES
      ('historical-slot', 'historical-day', 'dinner',
       'Исторический ужин', 0, true)
    """,
    """
    INSERT INTO meal_slot_dishes (
      id, meal_slot_id, dish_id, recipe_id, "order"
    ) VALUES
      ('historical-assignment', 'historical-slot',
       'dish-prohibited-default', 'recipe-prohibited-component', 0)
    """,
)


def _alembic_config() -> Config:
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    return config


def _engine(database_url: str) -> sa.Engine:
    return sa.create_engine(database_url)


def _current_revision(database_url: str) -> str | None:
    engine = _engine(database_url)
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
    engine = _engine(database_url)
    try:
        with engine.begin() as connection:
            for statement in SEED_STATEMENTS:
                connection.execute(sa.text(statement))
    finally:
        engine.dispose()


def _flag_rows(engine: sa.Engine, table_name: str) -> dict[str, tuple[bool, bool]]:
    with engine.connect() as connection:
        rows = connection.execute(
            sa.text(
                f"SELECT id, is_archived, archived_by_alcohol_policy "
                f"FROM {table_name}"
            )
        ).mappings()
        return {
            str(row["id"]): (
                bool(row["is_archived"]),
                bool(row["archived_by_alcohol_policy"]),
            )
            for row in rows
        }


def _active_ids(engine: sa.Engine, table_name: str) -> list[str]:
    with engine.connect() as connection:
        return sorted(
            str(value)
            for value in connection.scalars(
                sa.text(f"SELECT id FROM {table_name} WHERE is_archived = false")
            )
        )


def _historical_assignment(engine: sa.Engine) -> dict[str, Any]:
    with engine.connect() as connection:
        row = connection.execute(
            sa.text(
                "SELECT msd.id, msd.dish_id, msd.recipe_id, "
                "d.name AS dish_name, r.name AS recipe_name "
                "FROM meal_slot_dishes AS msd "
                "JOIN dishes AS d ON d.id = msd.dish_id "
                "JOIN recipes AS r ON r.id = msd.recipe_id "
                "WHERE msd.id = 'historical-assignment'"
            )
        ).mappings().one()
        return dict(row)


def _verify_h10021(database_url: str) -> dict[str, Any]:
    engine = _engine(database_url)
    try:
        expected = {
            "products": {
                "product-vodka": (True, True),
                "product-chamomile": (False, False),
                "product-vinegar": (False, False),
            },
            "recipes": {
                "recipe-prohibited-component": (True, True),
                "recipe-prohibited-name": (True, True),
                "recipe-allowed": (False, False),
                "recipe-manual-archive": (True, False),
            },
            "dishes": {
                "dish-prohibited-default": (True, True),
                "dish-prohibited-name": (True, True),
                "dish-allowed": (False, False),
                "dish-non-default-variant": (False, False),
            },
        }
        for table_name, table_expected in expected.items():
            actual = _flag_rows(engine, table_name)
            if actual != table_expected:
                raise AssertionError(
                    f"Unexpected {table_name} archive flags: {actual}"
                )

        active = {
            "products": _active_ids(engine, "products"),
            "recipes": _active_ids(engine, "recipes"),
            "dishes": _active_ids(engine, "dishes"),
        }
        expected_active = {
            "products": ["product-chamomile", "product-vinegar"],
            "recipes": ["recipe-allowed"],
            "dishes": ["dish-allowed", "dish-non-default-variant"],
        }
        if active != expected_active:
            raise AssertionError(f"Unexpected active catalogue rows: {active}")

        with engine.connect() as connection:
            variant_position = connection.scalar(
                sa.text(
                    "SELECT position FROM dish_recipe_variants "
                    "WHERE dish_id = 'dish-non-default-variant' "
                    "AND recipe_id = 'recipe-prohibited-name'"
                )
            )
        if variant_position != 1:
            raise AssertionError("Non-default historical Recipe variant changed")

        historical = _historical_assignment(engine)
        if historical["dish_id"] != "dish-prohibited-default":
            raise AssertionError("Historical Dish reference changed")
        if historical["recipe_id"] != "recipe-prohibited-component":
            raise AssertionError("Historical Recipe reference changed")

        return {
            "active_catalogue": active,
            "historical_assignment": historical,
            "non_default_variant_position": variant_position,
        }
    finally:
        engine.dispose()


def _column_names(engine: sa.Engine, table_name: str) -> set[str]:
    return {
        str(column["name"])
        for column in sa.inspect(engine).get_columns(table_name)
    }


def _verify_h10020_after_downgrade(database_url: str) -> dict[str, Any]:
    engine = _engine(database_url)
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

        with engine.connect() as connection:
            rows = connection.execute(
                sa.text("SELECT id, is_archived FROM recipes")
            ).mappings()
            archive_state = {
                str(row["id"]): bool(row["is_archived"])
                for row in rows
            }
        expected = {
            "recipe-prohibited-component": False,
            "recipe-prohibited-name": False,
            "recipe-allowed": False,
            "recipe-manual-archive": True,
        }
        if archive_state != expected:
            raise AssertionError(
                f"Unexpected downgraded Recipe archive state: {archive_state}"
            )
        return {
            "recipe_archive_state": archive_state,
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
        evidence["steps"].append(
            {
                "revision": HEAD_REVISION,
                "phase": "first_upgrade",
                **_verify_h10021(database_url),
            }
        )

        command.downgrade(config, PREVIOUS_REVISION)
        _assert_revision(database_url, PREVIOUS_REVISION)
        evidence["steps"].append(
            {
                "revision": PREVIOUS_REVISION,
                "phase": "downgrade",
                **_verify_h10020_after_downgrade(database_url),
            }
        )

        command.upgrade(config, HEAD_REVISION)
        _assert_revision(database_url, HEAD_REVISION)
        evidence["steps"].append(
            {
                "revision": HEAD_REVISION,
                "phase": "second_upgrade",
                **_verify_h10021(database_url),
            }
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
