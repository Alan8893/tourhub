from collections.abc import Mapping
from typing import cast
from uuid import uuid4

from app.models.equipment_list import EquipmentListORM
from app.models.equipment_list_item import EquipmentListItemORM
from app.models.meal_plan import MealPlanORM
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM
from app.models.user import UserORM
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.services.operational_audit_service import OperationalAuditService


class EquipmentListService:
    def __init__(
        self,
        repository: EquipmentListRepository,
        meal_plan_repository: MealPlanRepository,
        actor: UserORM | None = None,
    ) -> None:
        self.repository = repository
        self.meal_plan_repository = meal_plan_repository
        self.actor = actor

    def create_from_meal_plan_id(
        self,
        meal_plan_id: str,
        project_id: int | None = None,
        *,
        commit: bool = True,
    ) -> EquipmentListORM:
        meal_plan = self.meal_plan_repository.get_with_details(meal_plan_id)
        if meal_plan is None:
            raise ValueError("Meal plan not found")
        resolved_project_id = project_id or meal_plan.project_id
        if resolved_project_id is None:
            raise ValueError("Project is required")

        audit = OperationalAuditService(self.repository.session)
        equipment_list = self.repository.get_by_project_id(resolved_project_id)
        before = (
            audit.equipment_list_snapshot(equipment_list)
            if equipment_list is not None
            else None
        )
        if equipment_list is None:
            equipment_list = EquipmentListORM(
                id=str(uuid4()),
                project_id=resolved_project_id,
                meal_plan_id=meal_plan_id,
                status="prepared",
            )
            self.repository.add(equipment_list)
        else:
            equipment_list.meal_plan_id = meal_plan_id
            equipment_list.status = "prepared"

        self._synchronize(equipment_list, meal_plan)
        if self.actor is not None:
            audit.record_equipment_list_generated(
                actor=self.actor,
                equipment_list=equipment_list,
                before=before,
            )
        self._finish_write(commit=commit)
        return equipment_list

    def refresh_existing(self, meal_plan: MealPlanORM) -> EquipmentListORM | None:
        if meal_plan.project_id is None:
            return None
        equipment_list = self.repository.get_by_project_id(meal_plan.project_id)
        if equipment_list is None:
            return None
        equipment_list.meal_plan_id = str(meal_plan.id)
        equipment_list.status = "prepared"
        self._synchronize(equipment_list, meal_plan)
        self.repository.flush()
        return equipment_list

    def get_by_project_id(self, project_id: int) -> EquipmentListORM | None:
        return self.repository.get_by_project_id(project_id)

    def add_manual_item(
        self,
        project_id: int,
        equipment_name: str,
        required_quantity: int,
    ) -> EquipmentListItemORM:
        equipment_list = self._require_list(project_id)
        normalized_name = self._normalize_name(equipment_name)
        existing = self._find_by_name(equipment_list, normalized_name)
        audit = OperationalAuditService(self.repository.session)
        before: Mapping[str, object] | None = None
        if existing is not None:
            if not existing.is_removed:
                raise ValueError("Equipment item already exists")
            before = audit.equipment_item_snapshot(existing)
            existing.is_removed = False
            existing.required_quantity = required_quantity
            item = existing
        else:
            item = EquipmentListItemORM(
                id=str(uuid4()),
                equipment_name=normalized_name,
                required_quantity=required_quantity,
                calculated_quantity=None,
                is_manual=True,
                is_removed=False,
            )
            equipment_list.items.append(item)
        if self.actor is not None:
            audit.record_equipment_item_added(
                actor=self.actor,
                item=item,
                before=before,
            )
        self._finish_write(commit=True)
        return item

    def update_item_quantity(
        self,
        project_id: int,
        item_id: str,
        required_quantity: int,
    ) -> EquipmentListItemORM:
        item = self._require_item(project_id, item_id)
        if item.is_removed:
            raise LookupError("Equipment item not found")
        audit = OperationalAuditService(self.repository.session)
        before = audit.equipment_item_snapshot(item)
        item.required_quantity = required_quantity
        if before == audit.equipment_item_snapshot(item):
            return item
        if self.actor is not None:
            audit.record_equipment_item_updated(
                actor=self.actor,
                item=item,
                before=before,
            )
        self._finish_write(commit=True)
        return item

    def delete_item(self, project_id: int, item_id: str) -> None:
        item = self._require_item(project_id, item_id)
        if item.is_removed:
            raise LookupError("Equipment item not found")
        audit = OperationalAuditService(self.repository.session)
        before = audit.equipment_item_snapshot(item)
        hard_delete = item.is_manual or item.calculated_quantity is None
        if hard_delete:
            self.repository.delete_item(item)
            after = None
        else:
            item.is_removed = True
            after = audit.equipment_item_snapshot(item)
        if self.actor is not None:
            audit.record_equipment_item_deleted(
                actor=self.actor,
                item_id=item_id,
                before=before,
                after=after,
            )
        self._finish_write(commit=True)

    def visible_items(
        self,
        equipment_list: EquipmentListORM,
    ) -> list[EquipmentListItemORM]:
        return [
            cast(EquipmentListItemORM, item)
            for item in equipment_list.items
            if not item.is_removed
        ]

    def _synchronize(
        self,
        equipment_list: EquipmentListORM,
        meal_plan: MealPlanORM,
    ) -> None:
        calculated = self._calculate(meal_plan)
        existing = {
            self._key(item.equipment_name): cast(EquipmentListItemORM, item)
            for item in equipment_list.items
        }

        for key, (name, quantity) in calculated.items():
            item = existing.get(key)
            if item is None:
                equipment_list.items.append(
                    EquipmentListItemORM(
                        id=str(uuid4()),
                        equipment_name=name,
                        required_quantity=quantity,
                        calculated_quantity=quantity,
                        is_manual=False,
                        is_removed=False,
                    )
                )
                continue

            old_calculated = item.calculated_quantity
            has_quantity_override = (
                old_calculated is not None
                and item.required_quantity != old_calculated
            )
            if item.is_manual:
                item.is_manual = False
                item.calculated_quantity = quantity
            else:
                item.calculated_quantity = quantity
                if not has_quantity_override:
                    item.required_quantity = quantity

        calculated_keys = set(calculated)
        for relationship_item in list(equipment_list.items):
            item = cast(EquipmentListItemORM, relationship_item)
            key = self._key(item.equipment_name)
            if key in calculated_keys or item.is_manual:
                continue
            old_calculated = item.calculated_quantity
            has_quantity_override = (
                old_calculated is not None
                and item.required_quantity != old_calculated
            )
            if item.is_removed:
                self.repository.delete_item(item)
            elif has_quantity_override:
                item.calculated_quantity = None
                item.is_manual = True
            else:
                self.repository.delete_item(item)

    def _calculate(self, meal_plan: MealPlanORM) -> dict[str, tuple[str, int]]:
        recipe_ids = self._recipe_ids(meal_plan)
        requirements = self.repository.list_requirements(recipe_ids)
        by_recipe: dict[str, list[RecipeEquipmentRequirementORM]] = {}
        for requirement in requirements:
            by_recipe.setdefault(requirement.recipe_id, []).append(requirement)

        calculated: dict[str, tuple[str, int]] = {}
        for group in self._meal_groups(meal_plan):
            current: dict[str, tuple[str, int]] = {}
            for recipe_id in group:
                for requirement in by_recipe.get(recipe_id, []):
                    name = requirement.equipment_name
                    key = self._key(name)
                    previous = current.get(key)
                    quantity = requirement.quantity + (previous[1] if previous else 0)
                    display_name = previous[0] if previous else name
                    current[key] = (display_name, quantity)
            for key, item in current.items():
                previous = calculated.get(key)
                if previous is None or item[1] > previous[1]:
                    calculated[key] = item
        return calculated

    def _require_list(self, project_id: int) -> EquipmentListORM:
        equipment_list = self.repository.get_by_project_id(project_id)
        if equipment_list is None:
            raise LookupError("Equipment list not found")
        return equipment_list

    def _require_item(self, project_id: int, item_id: str) -> EquipmentListItemORM:
        equipment_list = self._require_list(project_id)
        for relationship_item in equipment_list.items:
            item = cast(EquipmentListItemORM, relationship_item)
            if item.id == item_id:
                return item
        raise LookupError("Equipment item not found")

    @classmethod
    def _find_by_name(
        cls,
        equipment_list: EquipmentListORM,
        equipment_name: str,
    ) -> EquipmentListItemORM | None:
        key = cls._key(equipment_name)
        for relationship_item in equipment_list.items:
            item = cast(EquipmentListItemORM, relationship_item)
            if cls._key(item.equipment_name) == key:
                return item
        return None

    @classmethod
    def _recipe_ids(cls, meal_plan: MealPlanORM) -> set[str]:
        result: set[str] = set()
        for group in cls._meal_groups(meal_plan):
            result.update(group)
        return result

    @staticmethod
    def _meal_groups(meal_plan: MealPlanORM) -> list[list[str]]:
        groups: list[list[str]] = []
        for day in meal_plan.days:
            if day.slots:
                for slot in day.slots:
                    groups.append([item.recipe_id for item in slot.dishes])
                continue
            by_type: dict[str, list[str]] = {}
            for item in day.items:
                by_type.setdefault(item.meal_type, []).append(item.recipe_id)
            groups.extend(by_type.values())
        return groups

    @staticmethod
    def _normalize_name(value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Equipment name must not be empty")
        return normalized

    @staticmethod
    def _key(value: str) -> str:
        return " ".join(value.split()).casefold()

    def _finish_write(self, *, commit: bool) -> None:
        try:
            if commit:
                self.repository.commit()
            else:
                self.repository.flush()
        except Exception:
            self.repository.session.rollback()
            raise
