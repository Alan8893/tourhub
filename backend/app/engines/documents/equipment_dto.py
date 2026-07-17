from dataclasses import dataclass


@dataclass(frozen=True)
class EquipmentDocumentItemDTO:
    equipment_name: str
    required_quantity: int
    calculated_quantity: int | None
    source: str


@dataclass(frozen=True)
class EquipmentDocumentDTO:
    equipment_list_id: str
    project_name: str
    title: str
    items: list[EquipmentDocumentItemDTO]
