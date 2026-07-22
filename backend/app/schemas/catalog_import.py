from typing import Literal

from pydantic import BaseModel, Field, model_validator

CatalogImportKind = Literal["products", "recipes"]
RecipeImportOwnership = Literal["club", "personal"]


class CatalogImportRequest(BaseModel):
    kind: CatalogImportKind
    content: str = Field(min_length=1)
    ownership_scope: RecipeImportOwnership | None = None

    @model_validator(mode="after")
    def validate_ownership_scope(self) -> "CatalogImportRequest":
        if self.kind == "recipes" and self.ownership_scope is None:
            raise ValueError("Для импорта рецептов выберите область владения.")
        if self.kind == "products" and self.ownership_scope is not None:
            raise ValueError("Область владения применяется только к рецептам.")
        return self


class CatalogImportApplyRequest(CatalogImportRequest):
    preview_token: str | None = Field(default=None, min_length=64, max_length=64)

    @model_validator(mode="after")
    def validate_preview_token(self) -> "CatalogImportApplyRequest":
        if self.kind == "recipes" and self.preview_token is None:
            raise ValueError("Сначала выполните проверку файла рецептов.")
        return self


class CatalogImportError(BaseModel):
    row: int
    field: str | None = None
    message: str


class CatalogImportResult(BaseModel):
    kind: CatalogImportKind
    valid: bool
    row_count: int = Field(ge=0)
    create_count: int = Field(ge=0)
    skip_count: int = Field(ge=0)
    component_count: int = Field(default=0, ge=0)
    note_count: int = Field(default=0, ge=0)
    ownership_scope: RecipeImportOwnership | None = None
    preview_token: str | None = None
    errors: list[CatalogImportError]
