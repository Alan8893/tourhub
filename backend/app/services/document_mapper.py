from app.engines.documents.dto import (
    DocumentItemDTO,
    PurchaseDocumentDTO,
)
from app.models.purchase_list import PurchaseListORM


class PurchaseDocumentMapper:
    """Map purchase domain objects into document DTOs."""

    def to_dto(
        self,
        purchase_list: PurchaseListORM,
    ) -> PurchaseDocumentDTO:
        return PurchaseDocumentDTO(
            purchase_list_id=purchase_list.id,
            title="Список закупки",
            items=[
                DocumentItemDTO(
                    product_name=item.product.name,
                    quantity=float(item.required_quantity),
                    unit=item.required_unit,
                    package_size=(
                        float(item.package_size)
                        if item.package_size is not None
                        else None
                    ),
                    packages_count=item.packages_count,
                )
                for item in purchase_list.items
            ],
        )
