from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recipe import RecipeORM
from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM
from app.policies.alcohol_policy import AlcoholPolicy
from app.services.audit_service import AuditService
from app.services.recipe_access_service import RecipeAccessService


class RecipeLifecycleService:
    def __init__(self, session: Session, actor: UserORM):
        self.session = session
        self.actor = actor

    def submit(self, recipe_id: str) -> RecipeORM:
        recipe = self._get_locked_recipe(recipe_id)
        RecipeAccessService.require_submittable(recipe, self.actor)
        AlcoholPolicy.require_recipe_content_allowed(recipe)
        before = self._snapshot(recipe)
        recipe.lifecycle_status = RecipeLifecycleStatus.SUBMITTED.value
        recipe.submitted_by_user_id = self.actor.id
        recipe.submitted_at = datetime.now(UTC)
        recipe.reviewed_by_user_id = None
        recipe.reviewed_at = None
        recipe.review_comment = None
        self._record(recipe, action="recipe_submitted", before=before)
        return self._commit_and_refresh(recipe)

    def publish(self, recipe_id: str) -> RecipeORM:
        recipe = self._get_locked_recipe(recipe_id)
        RecipeAccessService.require_reviewable(recipe, self.actor)
        AlcoholPolicy.require_recipe_content_allowed(recipe)
        before = self._snapshot(recipe)
        recipe.scope = RecipeScope.CLUB.value
        recipe.owner_user_id = None
        recipe.lifecycle_status = RecipeLifecycleStatus.PUBLISHED.value
        recipe.reviewed_by_user_id = self.actor.id
        recipe.reviewed_at = datetime.now(UTC)
        recipe.review_comment = None
        self._record(recipe, action="recipe_published", before=before)
        return self._commit_and_refresh(recipe)

    def reject(self, recipe_id: str, comment: str) -> RecipeORM:
        recipe = self._get_locked_recipe(recipe_id)
        RecipeAccessService.require_reviewable(recipe, self.actor)
        normalized_comment = " ".join(comment.split())
        if not normalized_comment:
            raise ValueError("Rejection comment must not be empty")
        before = self._snapshot(recipe)
        recipe.lifecycle_status = RecipeLifecycleStatus.REJECTED.value
        recipe.reviewed_by_user_id = self.actor.id
        recipe.reviewed_at = datetime.now(UTC)
        recipe.review_comment = normalized_comment
        self._record(recipe, action="recipe_rejected", before=before)
        return self._commit_and_refresh(recipe)

    def _get_locked_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self.session.scalar(
            select(RecipeORM).where(RecipeORM.id == recipe_id).with_for_update()
        )
        if recipe is None:
            raise LookupError("Recipe not found")
        return recipe

    def _record(
        self,
        recipe: RecipeORM,
        *,
        action: str,
        before: dict[str, object],
    ) -> None:
        AuditService(self.session).record(
            actor=self.actor,
            action=action,
            entity_type="recipe",
            entity_id=recipe.id,
            before=before,
            after=self._snapshot(recipe),
            context={"recipe_name": recipe.name},
        )

    @staticmethod
    def _snapshot(recipe: RecipeORM) -> dict[str, object]:
        return {
            "name": recipe.name,
            "scope": recipe.scope,
            "owner_user_id": recipe.owner_user_id,
            "lifecycle_status": recipe.lifecycle_status,
            "submitted_by_user_id": recipe.submitted_by_user_id,
            "submitted_at": recipe.submitted_at,
            "reviewed_by_user_id": recipe.reviewed_by_user_id,
            "reviewed_at": recipe.reviewed_at,
            "review_comment": recipe.review_comment,
            "is_archived": recipe.is_archived,
        }

    def _commit_and_refresh(self, recipe: RecipeORM) -> RecipeORM:
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(recipe)
        _ = recipe.owner
        _ = recipe.submitted_by
        _ = recipe.reviewed_by
        return recipe
