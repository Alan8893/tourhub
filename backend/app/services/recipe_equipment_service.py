from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recipe import RecipeORM
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM
from app.models.user import UserORM
from app.services.recipe_access_service import RecipeAccessService
from app.services.recipe_equipment_recalculation_service import (
    RecipeEquipmentRecalculationService,
)


class RecipeEquipmentService:
    def __init__(
        self,
        session: Session,
        recalculation_service: RecipeEquipmentRecalculationService | None = None,
        actor: UserORM | None = None,
    ) -> None:
        self.session = session
        self.actor = actor
        self.recalculation_service = recalculation_service or RecipeEquipmentRecalculationService(
            session
        )

    def list(self, recipe_id: str) -> list[RecipeEquipmentRequirementORM]:
        self._get_recipe(recipe_id)
        statement = (
            select(RecipeEquipmentRequirementORM)
            .where(RecipeEquipmentRequirementORM.recipe_id == recipe_id)
            .order_by(RecipeEquipmentRequirementORM.equipment_name)
        )
        return list(self.session.scalars(statement).all())

    def add(
        self,
        recipe_id: str,
        equipment_name: str,
        quantity: int,
    ) -> RecipeEquipmentRequirementORM:
        self._get_editable_recipe(recipe_id)
        normalized = self._normalize_name(equipment_name)
        self._ensure_unique(recipe_id, normalized)
        requirement = RecipeEquipmentRequirementORM(
            id=str(uuid4()),
            recipe_id=recipe_id,
            equipment_name=normalized,
            quantity=quantity,
        )
        self.session.add(requirement)
        self._commit(recipe_id)
        self.session.refresh(requirement)
        return requirement

    def update(
        self,
        recipe_id: str,
        requirement_id: str,
        equipment_name: str,
        quantity: int,
    ) -> RecipeEquipmentRequirementORM:
        self._get_editable_recipe(recipe_id)
        requirement = self._get_requirement(recipe_id, requirement_id)
        normalized = self._normalize_name(equipment_name)
        self._ensure_unique(recipe_id, normalized, exclude_id=requirement_id)
        requirement.equipment_name = normalized
        requirement.quantity = quantity
        self._commit(recipe_id)
        self.session.refresh(requirement)
        return requirement

    def delete(self, recipe_id: str, requirement_id: str) -> None:
        self._get_editable_recipe(recipe_id)
        requirement = self._get_requirement(recipe_id, requirement_id)
        self.session.delete(requirement)
        self._commit(recipe_id)

    def _get_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self.session.get(RecipeORM, recipe_id)
        if recipe is None:
            raise LookupError("Recipe not found")
        return RecipeAccessService.require_visible(recipe, self.actor)

    def _get_editable_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self._get_recipe(recipe_id)
        return RecipeAccessService.require_editable(recipe, self.actor)

    def _get_requirement(
        self,
        recipe_id: str,
        requirement_id: str,
    ) -> RecipeEquipmentRequirementORM:
        requirement = self.session.get(RecipeEquipmentRequirementORM, requirement_id)
        if requirement is None or requirement.recipe_id != recipe_id:
            raise LookupError("Equipment requirement not found")
        return requirement

    def _ensure_unique(
        self,
        recipe_id: str,
        equipment_name: str,
        exclude_id: str | None = None,
    ) -> None:
        normalized_key = equipment_name.casefold()
        for requirement in self.list(recipe_id):
            if requirement.id == exclude_id:
                continue
            if requirement.equipment_name.casefold() == normalized_key:
                raise ValueError("Equipment requirement already exists")

    @staticmethod
    def _normalize_name(value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Equipment name must not be empty")
        return normalized

    def _commit(self, recipe_id: str) -> None:
        try:
            self.session.flush()
            self.recalculation_service.refresh_affected_meal_plans(recipe_id)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
