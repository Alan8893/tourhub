from uuid import uuid4

from app.models.equipment_list import EquipmentListORM
from app.models.equipment_list_item import EquipmentListItemORM
from app.models.meal_plan import MealPlanORM
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository


class EquipmentListService:
    def __init__(
        self,
        repository: EquipmentListRepository,
        meal_plan_repository: MealPlanRepository,
    ) -> None:
        self.repository = repository
        self.meal_plan_repository = meal_plan_repository

    def create_from_meal_plan_id(
        self,
        meal_plan_id: str,
        project_id: int | None = None,
    ) -> EquipmentListORM:
        meal_plan = self.meal_plan_repository.get_with_details(meal_plan_id)
        if meal_plan is None:
            raise ValueError("Meal plan not found")
        resolved_project_id = project_id or meal_plan.project_id
        if resolved_project_id is None:
            raise ValueError("Project is required")

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

        equipment_list = self.repository.get_by_project_id(resolved_project_id)
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
            equipment_list.items.clear()
            self.repository.flush()

        for name, quantity in sorted(
            calculated.values(),
            key=lambda item: item[0].casefold(),
        ):
            equipment_list.items.append(
                EquipmentListItemORM(
                    id=str(uuid4()),
                    equipment_name=name,
                    required_quantity=quantity,
                )
            )

        self.repository.commit()
        return equipment_list

    def get_by_project_id(self, project_id: int) -> EquipmentListORM | None:
        return self.repository.get_by_project_id(project_id)

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
                    groups.append([item.dish.recipe_id for item in slot.dishes])
                continue
            by_type: dict[str, list[str]] = {}
            for item in day.items:
                by_type.setdefault(item.meal_type, []).append(item.dish.recipe_id)
            groups.extend(by_type.values())
        return groups

    @staticmethod
    def _key(value: str) -> str:
        return " ".join(value.split()).casefold()
