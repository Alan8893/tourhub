from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleMealTypeORM, DishMealRoleORM
from app.models.dish_recipe_variant import DishRecipeVariantORM
from app.models.recipe import RecipeORM
from app.models.user import UserORM
from app.services.published_recipe_dish_sync_service import (
    PublishedRecipeDishSyncService,
)
from app.services.recipe_lifecycle_service import RecipeLifecycleService


def published_recipe(recipe_id: str, name: str) -> RecipeORM:
    return RecipeORM(
        id=recipe_id,
        name=name,
        scope="club",
        lifecycle_status="published",
    )


def test_sync_creates_one_unclassified_dish_and_is_idempotent(db_session) -> None:
    recipe = published_recipe("recipe-new-dish", "Походная каша")
    db_session.add(recipe)
    db_session.commit()

    service = PublishedRecipeDishSyncService(db_session)
    first = service.synchronize(recipe)
    second = service.synchronize(recipe)
    db_session.commit()

    dishes = list(db_session.scalars(select(DishORM)).all())
    assert [dish.id for dish in dishes] == [first.id]
    assert second.id == first.id
    assert first.name == recipe.name
    assert first.recipe_id == recipe.id
    assert first.meal_roles == []
    assert [(variant.recipe_id, variant.position) for variant in first.recipe_variants] == [
        (recipe.id, 0)
    ]


def test_sync_attaches_same_name_recipe_without_replacing_default_or_roles(db_session) -> None:
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
    db_session.add_all([default_recipe, published, dish])
    db_session.commit()

    synchronized = PublishedRecipeDishSyncService(db_session).synchronize(published)
    db_session.commit()

    assert synchronized.id == dish.id
    assert synchronized.recipe_id == default_recipe.id
    assert [(variant.recipe_id, variant.position) for variant in synchronized.recipe_variants] == [
        (default_recipe.id, 0),
        (published.id, 1),
    ]
    assert len(synchronized.meal_roles) == 1
    assert synchronized.meal_roles[0].role == "main"
    assert [item.meal_type for item in synchronized.meal_roles[0].meal_types] == ["dinner"]


def test_publication_rolls_back_recipe_dish_and_audit_when_sync_fails(
    db_session,
    monkeypatch,
) -> None:
    owner = UserORM(
        email="owner-sync@example.org",
        display_name="Автор",
        role="instructor",
        password_hash="not-used",
        is_active=True,
    )
    reviewer = UserORM(
        email="reviewer-sync@example.org",
        display_name="Проверяющий",
        role="verified_instructor",
        password_hash="not-used",
        is_active=True,
    )
    db_session.add_all([owner, reviewer])
    db_session.flush()
    recipe = RecipeORM(
        id="recipe-rollback-sync",
        name="Рецепт с откатом",
        scope="personal",
        owner_user_id=owner.id,
        lifecycle_status="submitted",
        submitted_by_user_id=owner.id,
        submitted_at=datetime.now(UTC),
    )
    db_session.add(recipe)
    db_session.commit()

    def fail_after_dish_flush(
        service: PublishedRecipeDishSyncService,
        current_recipe: RecipeORM,
    ) -> DishORM:
        dish = DishORM(
            id="dish-must-rollback",
            name=current_recipe.name,
            recipe_id=current_recipe.id,
        )
        service.session.add(dish)
        service.session.flush()
        raise RuntimeError("synchronization failed")

    monkeypatch.setattr(PublishedRecipeDishSyncService, "synchronize", fail_after_dish_flush)

    with pytest.raises(RuntimeError, match="synchronization failed"):
        RecipeLifecycleService(db_session, actor=reviewer).publish(recipe.id)

    db_session.expire_all()
    stored = db_session.get(RecipeORM, recipe.id)
    assert stored is not None
    assert stored.scope == "personal"
    assert stored.owner_user_id == owner.id
    assert stored.lifecycle_status == "submitted"
    assert stored.reviewed_by_user_id is None
    assert db_session.get(DishORM, "dish-must-rollback") is None
