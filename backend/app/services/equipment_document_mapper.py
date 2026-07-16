from typing import cast

from app.engines.documents.equipment_dto import (
    EquipmentDocumentDTO,
    EquipmentDocumentItemDTO,
)
from app.models.equipment_list import EquipmentListORM
from app.models.equipment_list_item import EquipmentListItemORM


class EquipmentDocumentMapper:
    """Map a prepared equipment list into a stable document contract."""

    def to_dto(
        self,
        equipment_list: EquipmentListORM,
        project_name: str,
    ) -> EquipmentDocumentDTO:
        items = cast(list[EquipmentListItemORM], equipment_list.items)
        visible_items = sorted(
            (item for item in items if not item.is_removed),
            key=lambda item: item.equipment_name.casefold(),
        )
        return EquipmentDocumentDTO(
            equipment_list_id=equipment_list.id,
            project_name=project_name,
            title="Список оборудования",
            items=[
                EquipmentDocumentItemDTO(
                    equipment_name=item.equipment_name,
                    required_quantity=item.required_quantity,
                    calculated_quantity=item.calculated_quantity,
                    source=self._source(item),
                )
                for item in visible_items
            ],
        )

    @staticmethod
    def _source(item: EquipmentListItemORM) -> str:
        if item.is_manual:
            return "Добавлено вручную"
        if (
            item.calculated_quantity is not None
            and item.required_quantity != item.calculated_quantity
        ):
            return "Изменено вручную"
        return "Расчёт"
