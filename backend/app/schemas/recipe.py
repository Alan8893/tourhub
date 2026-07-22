from pydantic import BaseModel, Field, model_validator

from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
from app.models.recipe_scope import RecipeScope


class RecipeOwnershipResponse(BaseModel):
    scope: RecipeScope
    owner_user_id: int | None
    owner_display_name: str | None
    is_owned_by_current_user: bool
    lifecycle_status: RecipeLifecycleStatus
    submitted_by_user_id: int | None
    submitted_by_display_name: str | None
    submitted_at: str | None
    reviewed_by_user_id: int | None
    reviewed_by_display_name: str | None
    reviewed_at: str | None
    review_comment: str | None
    can_edit: bool
    can_archive: bool
    can_restore: bool
    can_delete: bool
    can_submit: bool
    can_publish: bool
    can_reject: bool


class RecipeListItemResponse(RecipeOwnershipResponse):
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


class ProductArchiveResponse(RecipeProductResponse):
    is_archived: bool
    archived_by_alcohol_policy: bool


class ProductArchiveListResponse(BaseModel):
    items: list[ProductArchiveResponse]


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    unit: str = Field(min_length=1, max_length=50)
    package_size: int | None = Field(default=None, gt=0)


class ProductUpdateRequest(ProductCreateRequest):
    pass


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


class RecipeDetailResponse(RecipeOwnershipResponse):
    id: str
    name: str
    is_archived: bool
    components: list[RecipeComponentResponse]
    notes: list[RecipeDetailNoteResponse]


class RecipeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class RecipeUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class RecipeRejectRequest(BaseModel):
    comment: str = Field(min_length=1, max_length=1000)


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


class RecipeWriteResponse(RecipeOwnershipResponse):
    id: str
    name: str
    is_archived: bool


class ProductListResponse(BaseModel):
    items: list[RecipeProductResponse]
