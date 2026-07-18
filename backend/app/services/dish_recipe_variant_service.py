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
            not recipe.is_archived
            and recipe.scope == RecipeScope.CLUB.value
            and recipe.lifecycle_status == RecipeLifecycleStatus.PUBLISHED.value
        )

    @staticmethod
    def is_personal_selectable(recipe: RecipeORM, actor: UserORM | None) -> bool:
        return (
            actor is not None
            and not recipe.is_archived
            and recipe.scope == RecipeScope.PERSONAL.value
            and recipe.owner_user_id == actor.id
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
        recipes = [variant.recipe for variant in dish.recipe_variants]
        if not recipes and dish.recipe is not None:
            recipes = [dish.recipe]
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
        club = cls._default_first(club, dish.recipe_id)
        personal = sorted(personal, key=cls._sort_key)

        generation_mode = RecipeGenerationMode(mode)
        if generation_mode == RecipeGenerationMode.CLUB_ONLY:
            return club
        if generation_mode == RecipeGenerationMode.PERSONAL_PREFERRED:
            return [*personal, *club]
        return [*club, *personal]

    @staticmethod
    def _sort_key(recipe: RecipeORM) -> tuple[str, str]:
        return (recipe.name.casefold(), recipe.id)

    @classmethod
    def _default_first(
        cls,
        recipes: Iterable[RecipeORM],
        default_recipe_id: str,
    ) -> list[RecipeORM]:
        ordered = sorted(recipes, key=cls._sort_key)
        return sorted(
            ordered,
            key=lambda recipe: (recipe.id != default_recipe_id, cls._sort_key(recipe)),
        )
