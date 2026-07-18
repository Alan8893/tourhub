from app.models.recipe import RecipeORM
from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM

ADMINISTRATOR = "administrator"
VERIFIED_INSTRUCTOR = "verified_instructor"


class RecipeAccessService:
    @staticmethod
    def can_open_moderation(actor: UserORM) -> bool:
        return actor.role in {ADMINISTRATOR, VERIFIED_INSTRUCTOR}

    @classmethod
    def can_view(cls, recipe: RecipeORM, actor: UserORM) -> bool:
        if actor.role == ADMINISTRATOR:
            return True
        if recipe.scope == RecipeScope.CLUB.value:
            return True
        if recipe.owner_user_id == actor.id:
            return True
        return (
            actor.role == VERIFIED_INSTRUCTOR
            and recipe.lifecycle_status == RecipeLifecycleStatus.SUBMITTED.value
        )

    @staticmethod
    def can_manage_scope(recipe: RecipeORM, actor: UserORM) -> bool:
        if actor.role == ADMINISTRATOR:
            return True
        if recipe.scope == RecipeScope.CLUB.value:
            return actor.role == VERIFIED_INSTRUCTOR
        return recipe.owner_user_id == actor.id

    @classmethod
    def can_edit(cls, recipe: RecipeORM, actor: UserORM) -> bool:
        if recipe.is_archived:
            return False
        if recipe.lifecycle_status == RecipeLifecycleStatus.SUBMITTED.value:
            return False
        if actor.role == ADMINISTRATOR:
            return True
        if recipe.scope == RecipeScope.CLUB.value:
            return actor.role == VERIFIED_INSTRUCTOR
        return (
            recipe.owner_user_id == actor.id
            and recipe.lifecycle_status
            in {
                RecipeLifecycleStatus.DRAFT.value,
                RecipeLifecycleStatus.REJECTED.value,
            }
        )

    @classmethod
    def can_archive(cls, recipe: RecipeORM, actor: UserORM) -> bool:
        if recipe.is_archived:
            return False
        if recipe.lifecycle_status == RecipeLifecycleStatus.SUBMITTED.value:
            return False
        return cls.can_manage_scope(recipe, actor)

    @classmethod
    def can_restore(cls, recipe: RecipeORM, actor: UserORM) -> bool:
        return recipe.is_archived and cls.can_manage_scope(recipe, actor)

    @staticmethod
    def can_delete(recipe: RecipeORM, actor: UserORM) -> bool:
        return actor.role == ADMINISTRATOR

    @staticmethod
    def can_submit(recipe: RecipeORM, actor: UserORM) -> bool:
        return (
            not recipe.is_archived
            and recipe.scope == RecipeScope.PERSONAL.value
            and recipe.owner_user_id == actor.id
            and recipe.lifecycle_status
            in {
                RecipeLifecycleStatus.DRAFT.value,
                RecipeLifecycleStatus.REJECTED.value,
            }
        )

    @staticmethod
    def can_review(recipe: RecipeORM, actor: UserORM) -> bool:
        if recipe.is_archived:
            return False
        if recipe.scope != RecipeScope.PERSONAL.value:
            return False
        if recipe.lifecycle_status != RecipeLifecycleStatus.SUBMITTED.value:
            return False
        if actor.role == ADMINISTRATOR:
            return True
        return actor.role == VERIFIED_INSTRUCTOR and recipe.owner_user_id != actor.id

    @classmethod
    def require_visible(cls, recipe: RecipeORM, actor: UserORM | None) -> RecipeORM:
        if actor is not None and not cls.can_view(recipe, actor):
            raise LookupError("Recipe not found")
        return recipe

    @classmethod
    def require_editable(cls, recipe: RecipeORM, actor: UserORM | None) -> RecipeORM:
        if actor is not None:
            cls.require_visible(recipe, actor)
        if recipe.is_archived:
            raise ValueError("Archived recipe cannot be edited")
        if recipe.lifecycle_status == RecipeLifecycleStatus.SUBMITTED.value:
            raise ValueError("Submitted recipe cannot be edited")
        if actor is not None and not cls.can_edit(recipe, actor):
            raise PermissionError("Recipe cannot be changed by the current user")
        return recipe

    @classmethod
    def require_archivable(cls, recipe: RecipeORM, actor: UserORM | None) -> RecipeORM:
        if actor is not None:
            cls.require_visible(recipe, actor)
        if recipe.lifecycle_status == RecipeLifecycleStatus.SUBMITTED.value:
            raise ValueError("Submitted recipe cannot be archived")
        if actor is not None and not cls.can_archive(recipe, actor):
            raise PermissionError("Recipe cannot be archived by the current user")
        return recipe

    @classmethod
    def require_restorable(cls, recipe: RecipeORM, actor: UserORM | None) -> RecipeORM:
        if actor is None:
            return recipe
        cls.require_visible(recipe, actor)
        if not cls.can_restore(recipe, actor):
            raise PermissionError("Recipe cannot be restored by the current user")
        return recipe

    @classmethod
    def require_submittable(cls, recipe: RecipeORM, actor: UserORM) -> RecipeORM:
        cls.require_visible(recipe, actor)
        if recipe.scope != RecipeScope.PERSONAL.value or recipe.owner_user_id != actor.id:
            raise PermissionError("Only the owner may submit a personal recipe")
        if recipe.is_archived:
            raise ValueError("Archived recipe cannot be submitted")
        if recipe.lifecycle_status not in {
            RecipeLifecycleStatus.DRAFT.value,
            RecipeLifecycleStatus.REJECTED.value,
        }:
            raise ValueError("Recipe cannot be submitted from its current state")
        return recipe

    @classmethod
    def require_reviewable(cls, recipe: RecipeORM, actor: UserORM) -> RecipeORM:
        if not cls.can_open_moderation(actor):
            raise PermissionError("Current user cannot moderate recipes")
        if recipe.is_archived:
            raise ValueError("Archived recipe cannot be moderated")
        if recipe.scope != RecipeScope.PERSONAL.value or (
            recipe.lifecycle_status != RecipeLifecycleStatus.SUBMITTED.value
        ):
            raise ValueError("Recipe is not awaiting moderation")
        if actor.role == VERIFIED_INSTRUCTOR and recipe.owner_user_id == actor.id:
            raise PermissionError("Verified instructor cannot review their own recipe")
        return recipe

    @classmethod
    def require_deletable(cls, recipe: RecipeORM, actor: UserORM | None) -> RecipeORM:
        if actor is not None and not cls.can_delete(recipe, actor):
            raise PermissionError("Only an administrator may permanently delete a recipe")
        return recipe
