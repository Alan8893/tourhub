from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dish import DishORM
from app.models.user import UserORM
from app.policies.alcohol_policy import AlcoholPolicy, AlcoholPolicyViolation
from app.services.audit_service import AuditService


class DishArchiveNotFoundError(RuntimeError):
    pass


class DishRestoreBlockedError(RuntimeError):
    pass


class DishArchiveService:
    def __init__(self, session: Session, *, actor: UserORM) -> None:
        self.session = session
        self.actor = actor

    def archive(self, dish_id: str) -> DishORM:
        try:
            dish = self._locked_dish(dish_id)
            if dish.is_archived:
                return dish

            before = self._snapshot(dish)
            dish.is_archived = True
            self._record_lifecycle(
                action="dish_archived",
                dish=dish,
                before=before,
            )
            self.session.commit()
            self.session.refresh(dish)
            return dish
        except Exception:
            self.session.rollback()
            raise

    def restore(self, dish_id: str) -> DishORM:
        try:
            dish = self._locked_dish(dish_id)
            if not dish.is_archived:
                return dish
            if dish.archived_by_alcohol_policy:
                raise DishRestoreBlockedError(
                    "Dish cannot be restored because it is blocked by the central alcohol policy"
                )

            try:
                AlcoholPolicy.require_dish_name_allowed(dish.name)
            except AlcoholPolicyViolation as error:
                raise DishRestoreBlockedError(
                    "Dish cannot be restored because it is blocked by the central alcohol policy"
                ) from error

            before = self._snapshot(dish)
            dish.is_archived = False
            self._record_lifecycle(
                action="dish_restored",
                dish=dish,
                before=before,
            )
            self.session.commit()
            self.session.refresh(dish)
            return dish
        except Exception:
            self.session.rollback()
            raise

    def _locked_dish(self, dish_id: str) -> DishORM:
        dish = self.session.scalar(
            select(DishORM).where(DishORM.id == dish_id).with_for_update()
        )
        if dish is None:
            raise DishArchiveNotFoundError("Dish not found")
        return dish

    @staticmethod
    def _snapshot(dish: DishORM) -> dict[str, object]:
        return {
            "name": dish.name,
            "recipe_id": dish.recipe_id,
            "is_archived": dish.is_archived,
        }

    def _record_lifecycle(
        self,
        *,
        action: str,
        dish: DishORM,
        before: dict[str, object],
    ) -> None:
        AuditService(self.session).record(
            actor=self.actor,
            action=action,
            entity_type="dish",
            entity_id=dish.id,
            before=before,
            after=self._snapshot(dish),
            context={
                "policy_locked": dish.archived_by_alcohol_policy,
            },
        )
