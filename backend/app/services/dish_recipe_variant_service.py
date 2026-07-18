from collections.abc import Iterable

from app.models.dish import DishORM
from app.models.recipe import RecipeORM
from app.models.recipe_generation_mode import RecipeGenerationMode
from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM


class DishRecipeVariantService:
    @staticmethod
    def is_club_selectable(recipe: RecipeORM) -> bool:
        return (
            not getattr(recipe, "is_archived", False)
            and getattr(recipe, "scope", RecipeScope.CLUB.value) == RecipeScope.CLUB.value
            and getattr(
                recipe,
                "lifecycle_status",
                RecipeLifecycleStatus.PUBLISHED.value,
            )
            == RecipeLifecycleStatus.PUBLISHED.value
        )

    @staticmethod
    def is_personal_selectable(recipe: RecipeORM, actor: UserORM | None) -> bool:
        return (
            actor is not None
            and not getattr(recipe, "is_archived", False)
            and getattr(recipe, "scope", RecipeScope.CLUB.value)
            == RecipeScope.PERSONAL.value
            and getattr(recipe, "owner_user_id", None) == actor.id
        )

    @classmethod
    def can_attach(cls, recipe: RecipeORM, actor: UserORM | None) -> bool:
        return cls.is_club_selectable(recipe) or cls.is_personal_selectable(recipe, actor)

    @classmethod
    def visible_recipes(
        cls,
        dish: DishORM,
        actor: UserORM | None,
    ) -> list[RecipeORM]:
        variants = getattr(dish, "recipe_variants", [])
        recipes = [variant.recipe for variant in variants]
        default_recipe = getattr(dish, "recipe", None)
        if not recipes and default_recipe is not None:
            default_recipe_id = getattr(dish, "recipe_id", "")
            if not getattr(default_recipe, "id", None) and default_recipe_id:
                default_recipe.id = default_recipe_id
            if not getattr(default_recipe, "name", None):
                default_recipe.name = getattr(dish, "name", default_recipe_id)
            recipes = [default_recipe]
        return [recipe for recipe in recipes if cls.can_attach(recipe, actor)]

    @classmethod
    def ordered_for_generation(
        cls,
        dish: DishORM,
        actor: UserORM | None,
        mode: str,
    ) -> list[RecipeORM]:
        recipes = cls.visible_recipes(dish, actor)
        club = [recipe for recipe in recipes if cls.is_club_selectable(recipe)]
        personal = [
            recipe for recipe in recipes if cls.is_personal_selectable(recipe, actor)
        ]
        default_recipe_id = getattr(dish, "recipe_id", "")
        club = cls._default_first(club, default_recipe_id)

        generation_mode = RecipeGenerationMode(mode)
        if generation_mode == RecipeGenerationMode.CLUB_ONLY:
            return club
        if generation_mode == RecipeGenerationMode.PERSONAL_PREFERRED:
            return [*personal, *club]
        return [*club, *personal]

    @staticmethod
    def recipe_id(recipe: RecipeORM, fallback: str = "") -> str:
        return str(getattr(recipe, "id", fallback))

    @classmethod
    def _default_first(
        cls,
        recipes: Iterable[RecipeORM],
        default_recipe_id: str,
    ) -> list[RecipeORM]:
        ordered = list(recipes)
        default = next(
            (
                recipe
                for recipe in ordered
                if cls.recipe_id(recipe, default_recipe_id) == default_recipe_id
            ),
            None,
        )
        if default is None:
            return ordered
        return [default, *(recipe for recipe in ordered if recipe is not default)]
