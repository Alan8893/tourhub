from pydantic import BaseModel, Field, model_validator


class RecipeListItemResponse(BaseModel):
    id: str
    name: str
    is_archived: bool
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


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    unit: str = Field(min_length=1, max_length=50)
    package_size: int | None = Field(default=None, gt=0)


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
    is_archived: bool
    components: list[RecipeComponentResponse]
    notes: list[RecipeDetailNoteResponse]


class RecipeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class RecipeUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class RecipeComponentWriteRequest(BaseModel):
    product_id: str = Field(min_length=1)
    component_type: str
    amount: int = Field(gt=0)
    unit: str = Field(min_length=1, max_length=50)
    calculation_type: str
    people_count: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_people_count(self) -> "RecipeComponentWriteRequest":
        if self.calculation_type == "package_per_people" and self.people_count is None:
            raise ValueError("people_count is required for package_per_people")
        return self


class RecipeWriteResponse(BaseModel):
    id: str
    name: str
    is_archived: bool


class ProductListResponse(BaseModel):
    items: list[RecipeProductResponse]
