from typing import Literal

from pydantic import BaseModel, Field


class BulkCsvImportRequest(BaseModel):
    content: str = Field(min_length=1)
    delimiter: Literal[",", ";", "\t"] = ";"
    dry_run: bool = True
    skip_existing: bool = True


class BulkImportIssue(BaseModel):
    row: int = Field(ge=2)
    message: str


class BulkImportResponse(BaseModel):
    dry_run: bool
    can_import: bool
    parsed_count: int = Field(ge=0)
    created_count: int = Field(ge=0)
    skipped_count: int = Field(ge=0)
    issues: list[BulkImportIssue]
