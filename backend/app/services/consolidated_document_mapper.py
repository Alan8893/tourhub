from collections.abc import Iterable
from typing import cast

from app.engines.documents.consolidated_dto import (
    ConsolidatedProjectDocumentDTO,
    EquipmentRowDTO,
    LoadoutRowDTO,
    MenuRowDTO,
    ProjectSummaryDTO,
    PurchaseRowDTO,
)
from app.models.equipment_list import EquipmentListORM
from app.models.equipment_list_item import EquipmentListItemORM
from app.models.meal_plan import MealPlanORM
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.modules.projects.models.project import ProjectORM
from app.services.equipment_document_mapper import EquipmentDocumentMapper

_MEAL_LABELS = {
    "breakfast": "Завтрак",
    "snack": "Перекус",
    "lunch": "Обед",
    "dinner": "Ужин",
}


class ConsolidatedDocumentMapper:
    """Map one prepared Project snapshot into the complete export contract."""

    def to_dto(
        self,
        *,
        project: ProjectORM,
        meal_plan: MealPlanORM,
        purchase_list: PurchaseListORM,
        equipment_list: EquipmentListORM,
        purchase_checklist: PurchaseChecklistORM | None,
    ) -> ConsolidatedProjectDocumentDTO:
        checklist_by_product = self._checklist_by_product(purchase_checklist)
        purchase_items = sorted(
            cast(list[PurchaseListItemORM], purchase_list.items),
            key=lambda item: (item.product.category.casefold(), item.product.name.casefold()),
        )

        comments = [
            item.note.strip()
            for item in checklist_by_product.values()
            if item.note is not None and item.note.strip()
        ]

        return ConsolidatedProjectDocumentDTO(
            summary=ProjectSummaryDTO(
                project_id=project.id,
                project_name=project.name,
                participants=project.participants,
                days=project.days,
                start_date=project.start_date,
                first_meal=project.first_meal,
                last_meal=project.last_meal,
                recipe_generation_mode=project.recipe_generation_mode,
                status=project.status,
            ),
            menu_rows=tuple(self._menu_rows(meal_plan)),
            loadout_rows=tuple(
                LoadoutRowDTO(
                    product_name=item.product.name,
                    category=item.product.category,
                    required_quantity=float(item.required_quantity),
                    required_unit=item.required_unit,
                )
                for item in purchase_items
            ),
            purchase_rows=tuple(
                self._purchase_row(item, checklist_by_product.get(item.product_id))
                for item in purchase_items
            ),
            equipment_rows=tuple(self._equipment_rows(equipment_list)),
            warnings=tuple(meal_plan.warnings or []),
            comments=tuple(dict.fromkeys(comments)),
            responsible_person=(
                purchase_list.responsible_person.strip()
                if purchase_list.responsible_person
                and purchase_list.responsible_person.strip()
                else None
            ),
        )

    @staticmethod
    def _checklist_by_product(
        purchase_checklist: PurchaseChecklistORM | None,
    ) -> dict[str, PurchaseChecklistItemORM]:
        if purchase_checklist is None:
            return {}
        items = cast(list[PurchaseChecklistItemORM], purchase_checklist.items)
        return {item.product_id: item for item in items}

    @staticmethod
    def _menu_rows(meal_plan: MealPlanORM) -> Iterable[MenuRowDTO]:
        for day in meal_plan.days:
            for slot in day.slots:
                meal_name = slot.name or _MEAL_LABELS.get(slot.meal_type, slot.meal_type)
                if not slot.dishes:
                    yield MenuRowDTO(
                        day_number=day.day_number,
                        meal_type=slot.meal_type,
                        meal_name=meal_name,
                        dish_name="—",
                        recipe_name="—",
                        is_manually_edited=slot.is_manually_edited,
                    )
                    continue
                for assignment in slot.dishes:
                    yield MenuRowDTO(
                        day_number=day.day_number,
                        meal_type=slot.meal_type,
                        meal_name=meal_name,
                        dish_name=assignment.dish.name,
                        recipe_name=assignment.recipe.name,
                        is_manually_edited=slot.is_manually_edited,
                    )

    @staticmethod
    def _purchase_row(
        item: PurchaseListItemORM,
        checklist_item: PurchaseChecklistItemORM | None,
    ) -> PurchaseRowDTO:
        return PurchaseRowDTO(
            product_name=item.product.name,
            category=item.product.category,
            required_quantity=float(item.required_quantity),
            required_unit=item.required_unit,
            package_size=float(item.package_size),
            package_unit=item.package_unit,
            packages_count=item.packages_count,
            purchase_quantity=float(item.purchase_quantity),
            surplus_quantity=float(item.surplus_quantity),
            purchased_quantity=(
                float(checklist_item.purchased_quantity)
                if checklist_item is not None
                else 0.0
            ),
            is_checked=checklist_item.is_checked if checklist_item is not None else False,
            comment=checklist_item.note if checklist_item is not None else None,
        )

    @staticmethod
    def _equipment_rows(equipment_list: EquipmentListORM) -> Iterable[EquipmentRowDTO]:
        items = cast(list[EquipmentListItemORM], equipment_list.items)
        visible_items = sorted(
            (item for item in items if not item.is_removed),
            key=lambda item: item.equipment_name.casefold(),
        )
        for item in visible_items:
            yield EquipmentRowDTO(
                equipment_name=item.equipment_name,
                required_quantity=item.required_quantity,
                calculated_quantity=item.calculated_quantity,
                source=EquipmentDocumentMapper._source(item),
            )
