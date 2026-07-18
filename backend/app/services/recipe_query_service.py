from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM
from app.services.recipe_access_service import ADMINISTRATOR, RecipeAccessService


class RecipeQueryService:
    def __init__(self, session: Session, actor: UserORM | None = None):
        self.session = session
        self.actor = actor

    def list_recipes(
        self,
        include_archived: bool = False,
        view: str = "library",
    ) -> list[RecipeORM]:
        statement = select(RecipeORM).options(
            selectinload(RecipeORM.owner),
            selectinload(RecipeORM.submitted_by),
            selectinload(RecipeORM.reviewed_by),
            selectinload(RecipeORM.components),
            selectinload(RecipeORM.notes),
        )
        if view == "moderation":
            if self.actor is None or not RecipeAccessService.can_open_moderation(self.actor):
                raise PermissionError("Current user cannot moderate recipes")
            statement = statement.where(
                RecipeORM.scope == RecipeScope.PERSONAL.value,
                RecipeORM.lifecycle_status == RecipeLifecycleStatus.SUBMITTED.value,
                RecipeORM.is_archived.is_(False),
            )
            if self.actor.role != ADMINISTRATOR:
                statement = statement.where(RecipeORM.owner_user_id != self.actor.id)
            statement = statement.order_by(RecipeORM.submitted_at, RecipeORM.name)
        else:
            if not include_archived:
                statement = statement.where(RecipeORM.is_archived.is_(False))
            if self.actor is not None and self.actor.role != ADMINISTRATOR:
                statement = statement.where(
                    or_(
                        RecipeORM.scope == RecipeScope.CLUB.value,
                        RecipeORM.owner_user_id == self.actor.id,
                    )
                )
            statement = statement.order_by(RecipeORM.name)
        return list(self.session.scalars(statement).all())

    def get_recipe(self, recipe_id: str) -> RecipeORM:
        statement = (
            select(RecipeORM)
            .where(RecipeORM.id == recipe_id)
            .options(
                selectinload(RecipeORM.owner),
                selectinload(RecipeORM.submitted_by),
                selectinload(RecipeORM.reviewed_by),
                selectinload(RecipeORM.components).selectinload(
                    RecipeComponentORM.product
                ),
                selectinload(RecipeORM.notes),
            )
        )
        recipe = self.session.scalar(statement)
        if recipe is None:
            raise ValueError("Recipe not found")
        try:
            return RecipeAccessService.require_visible(recipe, self.actor)
        except LookupError as error:
            raise ValueError(str(error)) from error
