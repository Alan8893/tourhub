from pydantic import BaseModel, Field


class RecipeListItemResponse(BaseModel):
    id: str
    name: str
    component_count: int = Field(ge=0)
    note_count: int = Field(ge=0)


class RecipeListResponse(BaseModel):
    items: list[RecipeListItemResponse]


class RecipeProductResponse(BaseModel):
    id: str
    name: str
    category: str | None
    unit: str
    package_size: int | None


class RecipeComponentResponse(BaseModel):
    id: str
    component_type: str
    amount: int = Field(gt=0)
    unit: str
    calculation_type: str
    people_count: int | None
    product: RecipeProductResponse


class RecipeDetailNoteResponse(BaseModel):
    id: str
    type: str
    text: str
    priority: int = Field(ge=0)
    created_at: str


class RecipeDetailResponse(BaseModel):
    id: str
    name: str
    components: list[RecipeComponentResponse]
    notes: list[RecipeDetailNoteResponse]
