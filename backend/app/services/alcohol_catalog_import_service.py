import csv
from io import StringIO

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import ProductORM
from app.policies.alcohol_policy import AlcoholPolicy, AlcoholPolicyViolation
from app.schemas.catalog_import import CatalogImportError, CatalogImportResult
from app.services.catalog_import_service import CatalogImportService


class AlcoholAwareCatalogImportService:
    """Apply the central alcohol policy around the existing CSV import workflow."""

    def __init__(self, session: Session):
        self.session = session
        self.base_service = CatalogImportService(session)

    def preview(self, kind: str, content: str) -> CatalogImportResult:
        result = self.base_service.preview(kind, content)
        errors = [*result.errors, *self._policy_errors(kind, content)]
        return result.model_copy(update={"valid": not errors, "errors": errors})

    def apply(self, kind: str, content: str) -> CatalogImportResult:
        preview = self.preview(kind, content)
        if not preview.valid:
            return preview
        return self.base_service.apply(kind, content)

    def _policy_errors(self, kind: str, content: str) -> list[CatalogImportError]:
        rows = self._rows(content)
        if rows is None:
            return []
        if kind == "products":
            return self._product_errors(rows)
        return self._recipe_errors(rows)

    @staticmethod
    def _rows(content: str) -> list[tuple[int, dict[str, str | None]]] | None:
        text = content.lstrip("\ufeff").strip()
        if not text:
            return None
        try:
            dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(StringIO(text), dialect=dialect)
        if not reader.fieldnames:
            return None
        return [(row_number, raw) for row_number, raw in enumerate(reader, start=2)]

    @staticmethod
    def _product_errors(
        rows: list[tuple[int, dict[str, str | None]]],
    ) -> list[CatalogImportError]:
        errors: list[CatalogImportError] = []
        for row_number, raw in rows:
            name = (raw.get("name") or "").strip()
            category = (raw.get("category") or "").strip() or None
            if not name:
                continue
            try:
                AlcoholPolicy.require_product_allowed(name=name, category=category)
            except AlcoholPolicyViolation as exc:
                errors.append(
                    CatalogImportError(
                        row=row_number,
                        field="name",
                        message=str(exc),
                    )
                )
        return errors

    def _recipe_errors(
        self,
        rows: list[tuple[int, dict[str, str | None]]],
    ) -> list[CatalogImportError]:
        archived_product_names = {
            name.casefold()
            for name in self.session.scalars(
                select(ProductORM.name).where(ProductORM.is_archived.is_(True))
            ).all()
        }
        errors: list[CatalogImportError] = []
        seen: set[tuple[int, str, str]] = set()
        for row_number, raw in rows:
            recipe_name = (raw.get("recipe_name") or "").strip()
            product_name = (raw.get("product_name") or "").strip()
            if recipe_name:
                try:
                    AlcoholPolicy.require_recipe_name_allowed(recipe_name)
                except AlcoholPolicyViolation as exc:
                    self._append_once(
                        errors,
                        seen,
                        row=row_number,
                        field="recipe_name",
                        message=str(exc),
                    )
            if product_name:
                try:
                    AlcoholPolicy.require_product_allowed(
                        name=product_name,
                        category=None,
                    )
                except AlcoholPolicyViolation as exc:
                    self._append_once(
                        errors,
                        seen,
                        row=row_number,
                        field="product_name",
                        message=str(exc),
                    )
                if product_name.casefold() in archived_product_names:
                    self._append_once(
                        errors,
                        seen,
                        row=row_number,
                        field="product_name",
                        message="Архивный продукт нельзя импортировать в рецепт.",
                    )
        return errors

    @staticmethod
    def _append_once(
        errors: list[CatalogImportError],
        seen: set[tuple[int, str, str]],
        *,
        row: int,
        field: str,
        message: str,
    ) -> None:
        key = (row, field, message)
        if key in seen:
            return
        seen.add(key)
        errors.append(CatalogImportError(row=row, field=field, message=message))
