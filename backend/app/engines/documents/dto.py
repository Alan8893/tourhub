from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DocumentItemDTO:
    product_name: str
    quantity: float
    unit: str
    package_size: float | None = None
    packages_count: int | None = None


@dataclass(frozen=True)
class PurchaseDocumentDTO:
    purchase_list_id: str
    title: str
    items: list[DocumentItemDTO]


@dataclass(frozen=True)
class GeneratedDocument:
    filename: str
    content_type: str
    generated_at: datetime
    content: bytes | str
