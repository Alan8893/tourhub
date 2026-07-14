from typing import Literal

from pydantic import BaseModel, Field


class CatalogImportRequest(BaseModel):
    kind: Literal["products", "recipes"]
    content: str = Field(min_length=1)


class CatalogImportError(BaseModel):
    row: int
    field: str | None = None
    message: str


class CatalogImportResult(BaseModel):
    kind: Literal["products", "recipes"]
    valid: bool
    row_count: int = Field(ge=0)
    create_count: int = Field(ge=0)
    skip_count: int = Field(ge=0)
    component_count: int = Field(default=0, ge=0)
    note_count: int = Field(default=0, ge=0)
    errors: list[CatalogImportError]
