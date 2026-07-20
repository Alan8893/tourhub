from collections.abc import Mapping
from typing import Literal

from sqlalchemy.orm import Session

from app.engines.documents.dto import GeneratedDocument
from app.models.equipment_list import EquipmentListORM
from app.models.equipment_list_item import EquipmentListItemORM
from app.models.product import ProductORM
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.models.purchase_list import PurchaseListORM
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM
from app.models.user import UserORM
from app.schemas.catalog_import import CatalogImportResult
from app.services.audit_service import AuditService


class OperationalAuditService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record_product_created(self, *, actor: UserORM, product: ProductORM) -> None:
        self._record(
            actor=actor,
            action="product_created",
            entity_type="product",
            entity_id=product.id,
            after=self.product_snapshot(product),
        )

    def record_product_updated(
        self,
        *,
        actor: UserORM,
        product: ProductORM,
        before: Mapping[str, object],
    ) -> None:
        self._record(
            actor=actor,
            action="product_updated",
            entity_type="product",
            entity_id=product.id,
            before=before,
            after=self.product_snapshot(product),
        )

    def record_catalog_import(
        self,
        *,
        actor: UserORM,
        result: CatalogImportResult,
    ) -> None:
        self._record(
            actor=actor,
            action="catalog_import_applied",
            entity_type="catalog_import",
            entity_id=result.kind,
            after={
                "kind": result.kind,
                "row_count": result.row_count,
                "create_count": result.create_count,
                "skip_count": result.skip_count,
                "component_count": result.component_count,
                "note_count": result.note_count,
            },
        )

    def record_purchase_list_generated(
        self,
        *,
        actor: UserORM,
        purchase_list: PurchaseListORM,
    ) -> None:
        self._record(
            actor=actor,
            action="purchase_list_generated",
            entity_type="purchase_list",
            entity_id=purchase_list.id,
            after=self.purchase_list_snapshot(purchase_list),
        )

    def record_purchase_list_updated(
        self,
        *,
        actor: UserORM,
        purchase_list: PurchaseListORM,
        before: Mapping[str, object],
    ) -> None:
        self._record(
            actor=actor,
            action="purchase_list_updated",
            entity_type="purchase_list",
            entity_id=purchase_list.id,
            before=before,
            after=self.purchase_list_snapshot(purchase_list),
        )

    def record_purchase_checklist_generated(
        self,
        *,
        actor: UserORM,
        checklist: PurchaseChecklistORM,
    ) -> None:
        self._record(
            actor=actor,
            action="purchase_checklist_generated",
            entity_type="purchase_checklist",
            entity_id=checklist.id,
            after=self.purchase_checklist_snapshot(checklist),
        )

    def record_purchase_checklist_item_updated(
        self,
        *,
        actor: UserORM,
        item: PurchaseChecklistItemORM,
        before: Mapping[str, object],
        checklist_status_before: str,
    ) -> None:
        self._record(
            actor=actor,
            action="purchase_checklist_item_updated",
            entity_type="purchase_checklist_item",
            entity_id=item.id,
            before=before,
            after=self.purchase_checklist_item_snapshot(item),
            context={
                "checklist_status_before": checklist_status_before,
                "checklist_status_after": item.checklist.status,
            },
        )

    def record_recipe_equipment_created(
        self,
        *,
        actor: UserORM,
        requirement: RecipeEquipmentRequirementORM,
    ) -> None:
        self._record(
            actor=actor,
            action="recipe_equipment_created",
            entity_type="recipe_equipment_requirement",
            entity_id=requirement.id,
            after=self.recipe_equipment_snapshot(requirement),
        )

    def record_recipe_equipment_updated(
        self,
        *,
        actor: UserORM,
        requirement: RecipeEquipmentRequirementORM,
        before: Mapping[str, object],
    ) -> None:
        self._record(
            actor=actor,
            action="recipe_equipment_updated",
            entity_type="recipe_equipment_requirement",
            entity_id=requirement.id,
            before=before,
            after=self.recipe_equipment_snapshot(requirement),
        )

    def record_recipe_equipment_deleted(
        self,
        *,
        actor: UserORM,
        requirement_id: str,
        before: Mapping[str, object],
    ) -> None:
        self._record(
            actor=actor,
            action="recipe_equipment_deleted",
            entity_type="recipe_equipment_requirement",
            entity_id=requirement_id,
            before=before,
        )

    def record_equipment_list_generated(
        self,
        *,
        actor: UserORM,
        equipment_list: EquipmentListORM,
        before: Mapping[str, object] | None,
    ) -> None:
        self._record(
            actor=actor,
            action="equipment_list_generated",
            entity_type="equipment_list",
            entity_id=equipment_list.id,
            before=before,
            after=self.equipment_list_snapshot(equipment_list),
        )

    def record_equipment_item_added(
        self,
        *,
        actor: UserORM,
        item: EquipmentListItemORM,
        before: Mapping[str, object] | None = None,
    ) -> None:
        self._record(
            actor=actor,
            action="equipment_list_item_added",
            entity_type="equipment_list_item",
            entity_id=item.id,
            before=before,
            after=self.equipment_item_snapshot(item),
        )

    def record_equipment_item_updated(
        self,
        *,
        actor: UserORM,
        item: EquipmentListItemORM,
        before: Mapping[str, object],
    ) -> None:
        self._record(
            actor=actor,
            action="equipment_list_item_updated",
            entity_type="equipment_list_item",
            entity_id=item.id,
            before=before,
            after=self.equipment_item_snapshot(item),
        )

    def record_equipment_item_deleted(
        self,
        *,
        actor: UserORM,
        item_id: str,
        before: Mapping[str, object],
        after: Mapping[str, object] | None,
    ) -> None:
        self._record(
            actor=actor,
            action="equipment_list_item_deleted",
            entity_type="equipment_list_item",
            entity_id=item_id,
            before=before,
            after=after,
        )

    def record_document_generated(
        self,
        *,
        actor: UserORM,
        source_entity_type: Literal["project", "purchase_list"],
        source_entity_id: str | int,
        document_kind: str,
        document_format: str,
        document: GeneratedDocument,
    ) -> None:
        self._record(
            actor=actor,
            action="document_generated",
            entity_type=f"{source_entity_type}_document",
            entity_id=source_entity_id,
            after={
                "document_kind": document_kind,
                "format": document_format,
                "content_type": document.content_type,
                "size_bytes": len(document.content),
            },
        )

    @staticmethod
    def product_snapshot(product: ProductORM) -> dict[str, object]:
        return {
            "name": product.name,
            "category": product.category,
            "unit": product.unit,
            "package_size": product.package_size,
            "is_archived": product.is_archived,
        }

    @staticmethod
    def purchase_list_snapshot(purchase_list: PurchaseListORM) -> dict[str, object]:
        return {
            "project_id": purchase_list.project_id,
            "meal_plan_id": purchase_list.meal_plan_id,
            "status": purchase_list.status,
            "responsible_person": purchase_list.responsible_person,
            "item_count": len(purchase_list.items),
            "packages_total": sum(item.packages_count for item in purchase_list.items),
        }

    @staticmethod
    def purchase_checklist_snapshot(
        checklist: PurchaseChecklistORM,
    ) -> dict[str, object]:
        return {
            "project_id": checklist.project_id,
            "meal_plan_id": checklist.meal_plan_id,
            "status": checklist.status,
            "item_count": len(checklist.items),
            "checked_item_count": sum(1 for item in checklist.items if item.is_checked),
        }

    @staticmethod
    def purchase_checklist_item_snapshot(
        item: PurchaseChecklistItemORM,
    ) -> dict[str, object]:
        return {
            "checklist_id": item.checklist_id,
            "product_id": item.product_id,
            "required_quantity": item.required_quantity,
            "purchased_quantity": item.purchased_quantity,
            "unit": item.unit,
            "is_checked": item.is_checked,
        }

    @staticmethod
    def recipe_equipment_snapshot(
        requirement: RecipeEquipmentRequirementORM,
    ) -> dict[str, object]:
        return {
            "recipe_id": requirement.recipe_id,
            "equipment_name": requirement.equipment_name,
            "quantity": requirement.quantity,
        }

    @staticmethod
    def equipment_list_snapshot(equipment_list: EquipmentListORM) -> dict[str, object]:
        items = list(equipment_list.items)
        return {
            "project_id": equipment_list.project_id,
            "meal_plan_id": equipment_list.meal_plan_id,
            "status": equipment_list.status,
            "visible_item_count": sum(1 for item in items if not item.is_removed),
            "manual_item_count": sum(
                1 for item in items if item.is_manual and not item.is_removed
            ),
            "overridden_item_count": sum(
                1
                for item in items
                if not item.is_removed
                and item.calculated_quantity is not None
                and item.required_quantity != item.calculated_quantity
            ),
            "removed_item_count": sum(1 for item in items if item.is_removed),
        }

    @staticmethod
    def equipment_item_snapshot(item: EquipmentListItemORM) -> dict[str, object]:
        return {
            "equipment_list_id": item.equipment_list_id,
            "equipment_name": item.equipment_name,
            "required_quantity": item.required_quantity,
            "calculated_quantity": item.calculated_quantity,
            "is_manual": item.is_manual,
            "is_removed": item.is_removed,
        }

    def _record(
        self,
        *,
        actor: UserORM,
        action: str,
        entity_type: str,
        entity_id: str | int,
        before: Mapping[str, object] | None = None,
        after: Mapping[str, object] | None = None,
        context: Mapping[str, object] | None = None,
    ) -> None:
        AuditService(self.session).record(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before=before,
            after=after,
            context=context,
        )
