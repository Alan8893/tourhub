from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectSummaryDTO:
    project_id: int
    project_name: str
    participants: int
    days: int
    start_date: str | None
    first_meal: str | None
    last_meal: str | None
    recipe_generation_mode: str
    status: str


@dataclass(frozen=True)
class MenuRowDTO:
    day_number: int
    meal_type: str
    meal_name: str
    dish_name: str
    recipe_name: str
    is_manually_edited: bool


@dataclass(frozen=True)
class LoadoutRowDTO:
    product_name: str
    category: str
    required_quantity: float
    required_unit: str


@dataclass(frozen=True)
class PurchaseRowDTO:
    product_name: str
    category: str
    required_quantity: float
    required_unit: str
    package_size: float
    package_unit: str
    packages_count: int
    purchase_quantity: float
    surplus_quantity: float
    purchased_quantity: float
    is_checked: bool
    comment: str | None


@dataclass(frozen=True)
class EquipmentRowDTO:
    equipment_name: str
    required_quantity: int
    calculated_quantity: int | None
    source: str


@dataclass(frozen=True)
class ConsolidatedProjectDocumentDTO:
    summary: ProjectSummaryDTO
    menu_rows: tuple[MenuRowDTO, ...]
    loadout_rows: tuple[LoadoutRowDTO, ...]
    purchase_rows: tuple[PurchaseRowDTO, ...]
    equipment_rows: tuple[EquipmentRowDTO, ...]
    warnings: tuple[str, ...]
    comments: tuple[str, ...]
    responsible_person: str | None
