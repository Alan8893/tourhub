from types import SimpleNamespace

from app.engines.meal_plan_generator import (
    DishInput,
    MealPlanGenerationResult,
    MealPlanItemResult,
    MealSlotResult,
)
from app.models.recipe import RecipeORM
from app.models.recipe_generation_mode import RecipeGenerationMode
from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM
from app.services.dish_recipe_variant_service import DishRecipeVariantService
from app.services.meal_plan_service import MealPlanService


def _recipe(
    recipe_id: str,
    name: str,
    *,
    scope: str = RecipeScope.CLUB.value,
    owner_user_id: int | None = None,
) -> RecipeORM:
    return RecipeORM(
        id=recipe_id,
        name=name,
        scope=scope,
        owner_user_id=owner_user_id,
        lifecycle_status=(
            RecipeLifecycleStatus.PUBLISHED.value
            if scope == RecipeScope.CLUB.value
            else RecipeLifecycleStatus.DRAFT.value
        ),
    )


def _actor(user_id: int = 7) -> UserORM:
    return UserORM(
        id=user_id,
        email=f"user-{user_id}@test.local",
        display_name=f"User {user_id}",
        role="instructor",
        password_hash="not-used",
        is_active=True,
    )


def _dish(default_recipe: RecipeORM, variants: list[RecipeORM]):
    return SimpleNamespace(
        id="dish-1",
        name="Porridge",
        recipe_id=default_recipe.id,
        recipe=default_recipe,
        recipe_variants=[SimpleNamespace(recipe=recipe) for recipe in variants],
    )


def test_generation_modes_order_visible_club_and_owned_personal_variants():
    actor = _actor()
    default_club = _recipe("club-default", "Club default")
    alternate_club = _recipe("club-alternate", "Club alternate")
    owned_personal = _recipe(
        "personal-owned",
        "My personal",
        scope=RecipeScope.PERSONAL.value,
        owner_user_id=actor.id,
    )
    unrelated_personal = _recipe(
        "personal-other",
        "Other personal",
        scope=RecipeScope.PERSONAL.value,
        owner_user_id=actor.id + 1,
    )
    dish = _dish(
        default_club,
        [alternate_club, unrelated_personal, owned_personal, default_club],
    )

    assert [
        recipe.id
        for recipe in DishRecipeVariantService.ordered_for_generation(
            dish,
            actor,
            RecipeGenerationMode.CLUB_ONLY.value,
        )
    ] == ["club-default", "club-alternate"]
    assert [
        recipe.id
        for recipe in DishRecipeVariantService.ordered_for_generation(
            dish,
            actor,
            RecipeGenerationMode.CLUB_AND_PERSONAL.value,
        )
    ] == ["club-default", "club-alternate", "personal-owned"]
    assert [
        recipe.id
        for recipe in DishRecipeVariantService.ordered_for_generation(
            dish,
            actor,
            RecipeGenerationMode.PERSONAL_PREFERRED.value,
        )
    ] == ["personal-owned", "club-default", "club-alternate"]


def test_assignment_rotation_persists_exact_recipe_per_occurrence():
    variants = [
        _recipe("recipe-a", "Recipe A"),
        _recipe("recipe-b", "Recipe B"),
    ]
    generated = MealPlanGenerationResult(
        items=[
            MealPlanItemResult(1, "breakfast", "dish-1", "Porridge"),
            MealPlanItemResult(2, "breakfast", "dish-1", "Porridge"),
            MealPlanItemResult(3, "breakfast", "dish-1", "Porridge"),
        ],
        slots=[
            MealSlotResult(1, "breakfast", [DishInput("dish-1", "Porridge")]),
            MealSlotResult(2, "breakfast", [DishInput("dish-1", "Porridge")]),
            MealSlotResult(3, "breakfast", [DishInput("dish-1", "Porridge")]),
        ],
    )

    result = MealPlanService._assign_recipe_variants(
        generated,
        {"dish-1": variants},
    )

    assert [item.recipe_id for item in result.items] == [
        "recipe-a",
        "recipe-b",
        "recipe-a",
    ]
    assert [slot.dishes[0].recipe_id for slot in result.slots] == [
        "recipe-a",
        "recipe-b",
        "recipe-a",
    ]


def test_preserved_manual_assignment_is_not_reselected():
    variants = [
        _recipe("recipe-a", "Recipe A"),
        _recipe("recipe-b", "Recipe B"),
    ]
    generated = MealPlanGenerationResult(
        items=[
            MealPlanItemResult(
                1,
                "dinner",
                "dish-1",
                "Porridge",
                recipe_id="historic-recipe",
            )
        ],
        slots=[
            MealSlotResult(
                1,
                "dinner",
                [DishInput("dish-1", "Porridge", recipe_id="historic-recipe")],
                is_manually_edited=True,
            )
        ],
    )

    result = MealPlanService._assign_recipe_variants(
        generated,
        {"dish-1": variants},
    )

    assert result.items[0].recipe_id == "historic-recipe"
    assert result.slots[0].dishes[0].recipe_id == "historic-recipe"
