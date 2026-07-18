from app.models.recipe import RecipeORM
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM

ADMINISTRATOR = "administrator"
VERIFIED_INSTRUCTOR = "verified_instructor"


class RecipeAccessService:
    @staticmethod
    def can_view(recipe: RecipeORM, actor: UserORM) -> bool:
        if actor.role == ADMINISTRATOR:
            return True
        if recipe.scope == RecipeScope.CLUB.value:
            return True
        return recipe.owner_user_id == actor.id

    @staticmethod
    def can_manage(recipe: RecipeORM, actor: UserORM) -> bool:
        if actor.role == ADMINISTRATOR:
            return True
        if recipe.scope == RecipeScope.CLUB.value:
            return actor.role == VERIFIED_INSTRUCTOR
        return recipe.owner_user_id == actor.id

    @classmethod
    def can_edit(cls, recipe: RecipeORM, actor: UserORM) -> bool:
        return not recipe.is_archived and cls.can_manage(recipe, actor)

    @staticmethod
    def can_delete(recipe: RecipeORM, actor: UserORM) -> bool:
        return actor.role == ADMINISTRATOR

    @classmethod
    def require_visible(cls, recipe: RecipeORM, actor: UserORM | None) -> RecipeORM:
        if actor is not None and not cls.can_view(recipe, actor):
            raise LookupError("Recipe not found")
        return recipe

    @classmethod
    def require_manageable(cls, recipe: RecipeORM, actor: UserORM | None) -> RecipeORM:
        if actor is not None and not cls.can_manage(recipe, actor):
            raise PermissionError("Recipe cannot be changed by the current user")
        return recipe

    @classmethod
    def require_editable(cls, recipe: RecipeORM, actor: UserORM | None) -> RecipeORM:
        cls.require_manageable(recipe, actor)
        if recipe.is_archived:
            raise ValueError("Archived recipe cannot be edited")
        return recipe

    @classmethod
    def require_deletable(cls, recipe: RecipeORM, actor: UserORM | None) -> RecipeORM:
        if actor is not None and not cls.can_delete(recipe, actor):
            raise PermissionError("Only an administrator may permanently delete a recipe")
        return recipe
