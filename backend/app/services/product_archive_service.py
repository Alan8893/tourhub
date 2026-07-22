from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import ProductORM
from app.models.user import UserORM
from app.policies.alcohol_policy import AlcoholPolicy, AlcoholPolicyViolation
from app.services.operational_audit_service import OperationalAuditService


class ProductArchiveNotFoundError(RuntimeError):
    pass


class ProductRestoreBlockedError(RuntimeError):
    pass


class ProductArchiveService:
    def __init__(self, session: Session, *, actor: UserORM) -> None:
        self.session = session
        self.actor = actor

    def archive(self, product_id: str) -> ProductORM:
        try:
            product = self._locked_product(product_id)
            if product.is_archived:
                return product

            audit = OperationalAuditService(self.session)
            before = audit.product_snapshot(product)
            product.is_archived = True
            audit.record_product_archived(
                actor=self.actor,
                product=product,
                before=before,
            )
            self.session.commit()
            self.session.refresh(product)
            return product
        except Exception:
            self.session.rollback()
            raise

    def restore(self, product_id: str) -> ProductORM:
        try:
            product = self._locked_product(product_id)
            if not product.is_archived:
                return product
            if product.archived_by_alcohol_policy:
                raise ProductRestoreBlockedError(
                    "Product cannot be restored because it is blocked by the central alcohol policy"
                )

            try:
                AlcoholPolicy.require_product_allowed(
                    name=product.name,
                    category=product.category,
                )
            except AlcoholPolicyViolation as error:
                raise ProductRestoreBlockedError(
                    "Product cannot be restored because it is blocked by the central alcohol policy"
                ) from error

            audit = OperationalAuditService(self.session)
            before = audit.product_snapshot(product)
            product.is_archived = False
            audit.record_product_restored(
                actor=self.actor,
                product=product,
                before=before,
            )
            self.session.commit()
            self.session.refresh(product)
            return product
        except Exception:
            self.session.rollback()
            raise

    def _locked_product(self, product_id: str) -> ProductORM:
        product = self.session.scalar(
            select(ProductORM).where(ProductORM.id == product_id).with_for_update()
        )
        if product is None:
            raise ProductArchiveNotFoundError("Product not found")
        return product
