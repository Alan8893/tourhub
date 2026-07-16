from pydantic import BaseModel, Field, field_validator


class RecipeEquipmentRequirementWriteRequest(BaseModel):
    equipment_name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(gt=0, le=9999)

    @field_validator("equipment_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("equipment_name must not be empty")
        return normalized


class RecipeEquipmentRequirementResponse(BaseModel):
    id: str
    recipe_id: str
    equipment_name: str
    quantity: int


class RecipeEquipmentRequirementListResponse(BaseModel):
    items: list[RecipeEquipmentRequirementResponse]


class EquipmentListItemWriteRequest(BaseModel):
    equipment_name: str = Field(min_length=1, max_length=255)
    required_quantity: int = Field(gt=0, le=9999)

    @field_validator("equipment_name")
    @classmethod
    def normalize_equipment_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("equipment_name must not be empty")
        return normalized


class EquipmentListItemQuantityRequest(BaseModel):
    required_quantity: int = Field(gt=0, le=9999)


class EquipmentListItemResponse(BaseModel):
    id: str
    equipment_name: str
    required_quantity: int
    calculated_quantity: int | None
    is_manual: bool
    is_overridden: bool


class EquipmentListResponse(BaseModel):
    id: str
    project_id: int
    meal_plan_id: str
    status: str
    items: list[EquipmentListItemResponse]
