from sqlalchemy.orm import Session

from app.models.equipment_list import EquipmentListORM
from app.models.equipment_list_item import EquipmentListItemORM
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM


class EquipmentListRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_project_id(self, project_id: int) -> EquipmentListORM | None:
        return (
            self.session.query(EquipmentListORM)
            .filter(EquipmentListORM.project_id == project_id)
            .first()
        )

    def get_by_meal_plan_id(self, meal_plan_id: str) -> EquipmentListORM | None:
        return (
            self.session.query(EquipmentListORM)
            .filter(EquipmentListORM.meal_plan_id == meal_plan_id)
            .first()
        )

    def list_requirements(
        self,
        recipe_ids: set[str],
    ) -> list[RecipeEquipmentRequirementORM]:
        if not recipe_ids:
            return []
        return list(
            self.session.query(RecipeEquipmentRequirementORM)
            .filter(RecipeEquipmentRequirementORM.recipe_id.in_(recipe_ids))
            .all()
        )

    def add(self, equipment_list: EquipmentListORM) -> None:
        self.session.add(equipment_list)

    def delete_item(self, item: EquipmentListItemORM) -> None:
        self.session.delete(item)

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.flush()
        self.session.commit()
