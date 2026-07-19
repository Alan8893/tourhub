from datetime import UTC, datetime

import pytest

from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
from app.models.user import UserORM
from app.policies.alcohol_policy import AlcoholPolicyViolation
from app.services.recipe_command_service import RecipeCommandService
from app.services.recipe_lifecycle_service import RecipeLifecycleService


def _user(*, email: str, role: str) -> UserORM:
    return UserORM(
        email=email,
        display_name=email.split("@", maxsplit=1)[0],
        role=role,
        password_hash="not-used",
        is_active=True,
    )


def _prohibited_product() -> ProductORM:
    return ProductORM(
        id="policy-vodka",
        name="Водка",
        category="Напитки",
        unit="millilitre",
        package_size=500,
    )


def _attach_product(recipe: RecipeORM, product: ProductORM) -> None:
    recipe.components.append(
        RecipeComponentORM(
            id=f"component-{recipe.id}",
            product=product,
            component_type="base",
            amount=10,
            unit="millilitre",
            calculation_type="per_person",
        )
    )


def test_submit_rejects_recipe_with_prohibited_existing_component(db_session) -> None:
    owner = _user(email="owner-policy@example.test", role="instructor")
    product = _prohibited_product()
    db_session.add_all([owner, product])
    db_session.flush()
    recipe = RecipeORM(
        id="policy-submit-recipe",
        name="Вечерний чай",
        scope="personal",
        owner_user_id=owner.id,
        lifecycle_status="draft",
    )
    _attach_product(recipe, product)
    db_session.add(recipe)
    db_session.commit()

    with pytest.raises(AlcoholPolicyViolation, match="Алкоголь запрещён"):
        RecipeLifecycleService(db_session, actor=owner).submit(recipe.id)

    db_session.refresh(recipe)
    assert recipe.lifecycle_status == "draft"
    assert recipe.submitted_at is None


def test_publish_rejects_submitted_recipe_with_prohibited_component(db_session) -> None:
    owner = _user(email="submitter-policy@example.test", role="instructor")
    reviewer = _user(email="reviewer-policy@example.test", role="administrator")
    product = _prohibited_product()
    db_session.add_all([owner, reviewer, product])
    db_session.flush()
    recipe = RecipeORM(
        id="policy-publish-recipe",
        name="Походный напиток",
        scope="personal",
        owner_user_id=owner.id,
        lifecycle_status="submitted",
        submitted_by_user_id=owner.id,
        submitted_at=datetime.now(UTC),
    )
    _attach_product(recipe, product)
    db_session.add(recipe)
    db_session.commit()

    with pytest.raises(AlcoholPolicyViolation, match="Алкоголь запрещён"):
        RecipeLifecycleService(db_session, actor=reviewer).publish(recipe.id)

    db_session.refresh(recipe)
    assert recipe.lifecycle_status == "submitted"
    assert recipe.scope == "personal"
    assert recipe.reviewed_at is None


def test_policy_archived_recipe_cannot_be_restored(db_session) -> None:
    administrator = _user(email="admin-policy@example.test", role="administrator")
    db_session.add(administrator)
    db_session.flush()
    recipe = RecipeORM(
        id="policy-archived-recipe",
        name="Исторический рецепт",
        scope="club",
        lifecycle_status="published",
        is_archived=True,
        archived_by_alcohol_policy=True,
    )
    db_session.add(recipe)
    db_session.commit()

    with pytest.raises(AlcoholPolicyViolation, match="не может быть восстановлен"):
        RecipeCommandService(db_session, actor=administrator).restore_recipe(recipe.id)

    db_session.refresh(recipe)
    assert recipe.is_archived is True
