import os
from collections.abc import Iterator
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base
from app.models.audit_event import AuditEventORM
from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleMealTypeORM, DishMealRoleORM
from app.models.dish_recipe_variant import DishRecipeVariantORM
from app.models.recipe import RecipeORM
from app.models.user import UserORM
from app.services.published_recipe_dish_sync_service import (
    PublishedRecipeDishSyncService,
)
from app.services.recipe_lifecycle_service import RecipeLifecycleService

# Production runs on PostgreSQL, which rejects row locks that SQLite silently
# ignores. Set this variable to run every scenario below against PostgreSQL too.
POSTGRES_URL_ENV = "TOURHUB_TEST_POSTGRES_URL"


@pytest.fixture
def postgres_engine():
    url = os.environ.get(POSTGRES_URL_ENV)
    if not url:
        pytest.skip(f"{POSTGRES_URL_ENV} is not set")
    engine = create_engine(url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(params=["sqlite", "postgresql"])
def sync_session(request) -> Iterator[Session]:
    if request.param == "sqlite":
        yield request.getfixturevalue("db_session")
        return
    engine = request.getfixturevalue("postgres_engine")
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def published_recipe(recipe_id: str, name: str) -> RecipeORM:
    return RecipeORM(
        id=recipe_id,
        name=name,
        scope="club",
        lifecycle_status="published",
    )


def add_owner_and_reviewer(session: Session, suffix: str) -> tuple[UserORM, UserORM]:
    owner = UserORM(
        email=f"owner-{suffix}@example.org",
        display_name="Автор",
        role="instructor",
        password_hash="not-used",
        is_active=True,
    )
    reviewer = UserORM(
        email=f"reviewer-{suffix}@example.org",
        display_name="Проверяющий",
        role="verified_instructor",
        password_hash="not-used",
        is_active=True,
    )
    session.add_all([owner, reviewer])
    session.flush()
    return owner, reviewer


def submitted_personal_recipe(recipe_id: str, name: str, owner: UserORM) -> RecipeORM:
    return RecipeORM(
        id=recipe_id,
        name=name,
        scope="personal",
        owner_user_id=owner.id,
        lifecycle_status="submitted",
        submitted_by_user_id=owner.id,
        submitted_at=datetime.now(UTC),
    )


def variant_rows(session: Session) -> list[tuple[str, str, int]]:
    return [
        (variant.dish_id, variant.recipe_id, variant.position)
        for variant in session.scalars(
            select(DishRecipeVariantORM).order_by(
                DishRecipeVariantORM.dish_id,
                DishRecipeVariantORM.position,
            )
        )
    ]


def test_attached_dish_lookup_locks_dishes_without_outer_join() -> None:
    session = MagicMock()

    PublishedRecipeDishSyncService(session)._find_attached_dish("recipe-id")

    statement = session.scalars.call_args.args[0]
    sql = str(statement.compile(dialect=postgresql.dialect()))
    assert "OUTER JOIN" not in sql
    assert "EXISTS (SELECT" in sql
    assert sql.rstrip().endswith("FOR UPDATE")


def test_publish_personal_recipe_creates_default_dish_and_is_idempotent(
    sync_session: Session,
) -> None:
    owner, reviewer = add_owner_and_reviewer(sync_session, "publish")
    recipe = submitted_personal_recipe("recipe-publish-new", "Походная каша", owner)
    sync_session.add(recipe)
    sync_session.commit()

    published = RecipeLifecycleService(sync_session, actor=reviewer).publish(recipe.id)

    assert published.scope == "club"
    assert published.lifecycle_status == "published"
    assert published.owner_user_id is None
    dishes = list(sync_session.scalars(select(DishORM)).all())
    assert len(dishes) == 1
    dish = dishes[0]
    assert dish.name == recipe.name
    assert dish.recipe_id == recipe.id
    assert variant_rows(sync_session) == [(dish.id, recipe.id, 0)]
    audit = sync_session.scalars(
        select(AuditEventORM).where(AuditEventORM.action == "recipe_published")
    ).one()
    assert audit.entity_id == recipe.id
    assert audit.context_data["dish_id"] == dish.id

    service = PublishedRecipeDishSyncService(sync_session)
    assert service.synchronize(published).id == dish.id
    assert service.synchronize(published).id == dish.id
    sync_session.commit()

    assert [item.id for item in sync_session.scalars(select(DishORM))] == [dish.id]
    assert variant_rows(sync_session) == [(dish.id, recipe.id, 0)]


def test_sync_creates_one_unclassified_dish_and_is_idempotent(sync_session: Session) -> None:
    recipe = published_recipe("recipe-new-dish", "Походная каша")
    sync_session.add(recipe)
    sync_session.commit()

    service = PublishedRecipeDishSyncService(sync_session)
    first = service.synchronize(recipe)
    second = service.synchronize(recipe)
    sync_session.commit()

    dishes = list(sync_session.scalars(select(DishORM)).all())
    assert [dish.id for dish in dishes] == [first.id]
    assert second.id == first.id
    assert first.name == recipe.name
    assert first.recipe_id == recipe.id
    assert first.meal_roles == []
    assert [(variant.recipe_id, variant.position) for variant in first.recipe_variants] == [
        (recipe.id, 0)
    ]


def test_sync_reuses_dish_attached_through_default_recipe(sync_session: Session) -> None:
    recipe = published_recipe("recipe-default-only", "Плов")
    dish = DishORM(id="dish-default-only", name="Плов в котле", recipe_id=recipe.id)
    sync_session.add_all([recipe, dish])
    sync_session.commit()

    synchronized = PublishedRecipeDishSyncService(sync_session).synchronize(recipe)
    sync_session.commit()

    assert synchronized.id == dish.id
    assert synchronized.recipe_id == recipe.id
    assert sync_session.scalar(select(func.count()).select_from(DishORM)) == 1
    assert variant_rows(sync_session) == []


def test_sync_reuses_dish_attached_through_variant(sync_session: Session) -> None:
    default_recipe = published_recipe("recipe-variant-default", "Гречка")
    variant_recipe = published_recipe("recipe-variant-only", "Гречка с тушёнкой")
    dish = DishORM(id="dish-with-variant", name="Гречка", recipe_id=default_recipe.id)
    dish.recipe_variants = [
        DishRecipeVariantORM(dish_id=dish.id, recipe_id=default_recipe.id, position=0),
        DishRecipeVariantORM(dish_id=dish.id, recipe_id=variant_recipe.id, position=1),
    ]
    sync_session.add_all([default_recipe, variant_recipe, dish])
    sync_session.commit()

    service = PublishedRecipeDishSyncService(sync_session)
    first = service.synchronize(variant_recipe)
    second = service.synchronize(variant_recipe)
    sync_session.commit()

    assert first.id == dish.id
    assert second.id == dish.id
    assert first.recipe_id == default_recipe.id
    assert sync_session.scalar(select(func.count()).select_from(DishORM)) == 1
    assert variant_rows(sync_session) == [
        (dish.id, default_recipe.id, 0),
        (dish.id, variant_recipe.id, 1),
    ]


def test_sync_attaches_same_name_recipe_without_replacing_default_or_roles(
    sync_session: Session,
) -> None:
    default_recipe = published_recipe("recipe-default", "Суп походный")
    published = published_recipe("recipe-new-variant", "Суп походный новый")
    dish = DishORM(
        id="dish-existing",
        name="Суп походный новый",
        recipe_id=default_recipe.id,
    )
    dish.recipe_variants = [
        DishRecipeVariantORM(
            dish_id=dish.id,
            recipe_id=default_recipe.id,
            position=0,
        )
    ]
    dish.meal_roles = [
        DishMealRoleORM(
            dish_id=dish.id,
            role="main",
            is_repeatable=False,
            meal_types=[
                DishMealRoleMealTypeORM(
                    dish_id=dish.id,
                    role="main",
                    meal_type="dinner",
                )
            ],
        )
    ]
    sync_session.add_all([default_recipe, published, dish])
    sync_session.commit()

    service = PublishedRecipeDishSyncService(sync_session)
    synchronized = service.synchronize(published)
    repeated = service.synchronize(published)
    sync_session.commit()

    assert synchronized.id == dish.id
    assert repeated.id == dish.id
    assert synchronized.recipe_id == default_recipe.id
    assert [(variant.recipe_id, variant.position) for variant in synchronized.recipe_variants] == [
        (default_recipe.id, 0),
        (published.id, 1),
    ]
    assert len(synchronized.meal_roles) == 1
    assert synchronized.meal_roles[0].role == "main"
    assert [item.meal_type for item in synchronized.meal_roles[0].meal_types] == ["dinner"]
    assert sync_session.scalar(select(func.count()).select_from(DishORM)) == 1


def test_attached_dish_row_stays_locked_until_publication_transaction_ends(
    postgres_engine,
) -> None:
    default_recipe = published_recipe("recipe-locked-default", "Рагу")
    recipe = published_recipe("recipe-locked", "Рагу овощное")
    dish = DishORM(id="dish-locked", name="Рагу", recipe_id=default_recipe.id)
    dish.recipe_variants = [
        DishRecipeVariantORM(dish_id=dish.id, recipe_id=default_recipe.id, position=0),
        DishRecipeVariantORM(dish_id=dish.id, recipe_id=recipe.id, position=1),
    ]
    with Session(postgres_engine, expire_on_commit=False) as setup:
        setup.add_all([default_recipe, recipe, dish])
        setup.commit()

    with Session(postgres_engine) as holder, postgres_engine.connect() as competitor:
        locked = PublishedRecipeDishSyncService(holder)._find_attached_dish(recipe.id)
        assert locked is not None
        assert locked.id == dish.id

        with pytest.raises(OperationalError, match="could not obtain lock"):
            competitor.execute(
                text("SELECT id FROM dishes WHERE id = :id FOR UPDATE NOWAIT"),
                {"id": dish.id},
            )
        competitor.rollback()

        holder.rollback()
        released = competitor.execute(
            text("SELECT id FROM dishes WHERE id = :id FOR UPDATE NOWAIT"),
            {"id": dish.id},
        ).scalar_one()
        assert released == dish.id
        competitor.rollback()


def test_publication_rolls_back_recipe_dish_and_audit_when_sync_fails(
    sync_session: Session,
    monkeypatch,
) -> None:
    owner, reviewer = add_owner_and_reviewer(sync_session, "sync")
    recipe = submitted_personal_recipe("recipe-rollback-sync", "Рецепт с откатом", owner)
    sync_session.add(recipe)
    sync_session.commit()

    def fail_after_dish_flush(
        service: PublishedRecipeDishSyncService,
        current_recipe: RecipeORM,
    ) -> DishORM:
        dish = DishORM(
            id="dish-must-rollback",
            name=current_recipe.name,
            recipe_id=current_recipe.id,
        )
        dish.recipe_variants = [
            DishRecipeVariantORM(dish_id=dish.id, recipe_id=current_recipe.id, position=0)
        ]
        service.session.add(dish)
        service.session.flush()
        raise RuntimeError("synchronization failed")

    monkeypatch.setattr(PublishedRecipeDishSyncService, "synchronize", fail_after_dish_flush)

    with pytest.raises(RuntimeError, match="synchronization failed"):
        RecipeLifecycleService(sync_session, actor=reviewer).publish(recipe.id)

    sync_session.expire_all()
    stored = sync_session.get(RecipeORM, recipe.id)
    assert stored is not None
    assert stored.scope == "personal"
    assert stored.owner_user_id == owner.id
    assert stored.lifecycle_status == "submitted"
    assert stored.reviewed_by_user_id is None
    assert sync_session.get(DishORM, "dish-must-rollback") is None
    assert variant_rows(sync_session) == []
    assert (
        sync_session.scalar(
            select(func.count())
            .select_from(AuditEventORM)
            .where(AuditEventORM.action == "recipe_published")
        )
        == 0
    )
