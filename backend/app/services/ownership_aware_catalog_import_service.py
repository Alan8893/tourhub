from hashlib import sha256
from hmac import compare_digest
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
from app.models.recipe_note import RecipeNoteORM
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM
from app.schemas.catalog_import import (
    CatalogImportKind,
    CatalogImportResult,
    RecipeImportOwnership,
)
from app.services.alcohol_catalog_import_service import (
    AlcoholAwareCatalogImportService,
)
from app.services.catalog_import_service import CatalogImportService
from app.services.operational_audit_service import OperationalAuditService


class OwnershipAwareCatalogImportService:
    """Apply Recipe ownership around the existing validated CSV import workflow."""

    def __init__(self, session: Session, *, actor: UserORM) -> None:
        self.session = session
        self.actor = actor
        self.alcohol_service = AlcoholAwareCatalogImportService(session, actor=actor)
        self.catalog_service = CatalogImportService(session, actor=actor)

    def preview(
        self,
        kind: CatalogImportKind,
        content: str,
        *,
        ownership_scope: RecipeImportOwnership | None,
    ) -> CatalogImportResult:
        result = self.alcohol_service.preview(kind, content)
        if kind == "products":
            return result
        resolved_scope = ownership_scope or RecipeScope.CLUB.value
        return result.model_copy(
            update={
                "ownership_scope": resolved_scope,
                "preview_token": self._preview_token(
                    kind=kind,
                    content=content,
                    ownership_scope=resolved_scope,
                ),
            }
        )

    def apply(
        self,
        kind: CatalogImportKind,
        content: str,
        *,
        ownership_scope: RecipeImportOwnership | None,
        preview_token: str | None,
    ) -> CatalogImportResult:
        if kind == "products":
            return self.alcohol_service.apply(kind, content)

        resolved_scope = ownership_scope or RecipeScope.CLUB.value
        preview = self.preview(
            kind,
            content,
            ownership_scope=resolved_scope,
        )
        legacy_club_apply = ownership_scope is None and preview_token is None
        expected_token = preview.preview_token or ""
        if not legacy_club_apply and (
            not preview_token or not compare_digest(preview_token, expected_token)
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Файл или область владения изменились после проверки. "
                    "Выполните проверку повторно."
                ),
            )
        if not preview.valid:
            return preview
        return self._apply_recipes(
            content,
            ownership_scope=resolved_scope,
            result=preview,
        )

    def _apply_recipes(
        self,
        content: str,
        *,
        ownership_scope: RecipeImportOwnership,
        result: CatalogImportResult,
    ) -> CatalogImportResult:
        try:
            recipe_rows, _ = self.catalog_service._parse_recipes(content)
            products = {
                product.name.casefold(): product
                for product in self.session.scalars(select(ProductORM)).all()
            }
            recipes: dict[str, RecipeORM] = {}
            notes: set[tuple[str, str, str, int]] = set()
            for recipe_row in recipe_rows:
                recipe_key = recipe_row.recipe_name.casefold()
                recipe = recipes.get(recipe_key)
                if recipe is None:
                    is_personal = ownership_scope == RecipeScope.PERSONAL.value
                    recipe = RecipeORM(
                        id=str(uuid4()),
                        name=recipe_row.recipe_name,
                        scope=ownership_scope,
                        owner_user_id=self.actor.id if is_personal else None,
                        lifecycle_status=(
                            RecipeLifecycleStatus.DRAFT.value
                            if is_personal
                            else RecipeLifecycleStatus.PUBLISHED.value
                        ),
                    )
                    recipes[recipe_key] = recipe
                    self.session.add(recipe)

                product = products[recipe_row.product_name.casefold()]
                self.session.add(
                    RecipeComponentORM(
                        id=str(uuid4()),
                        recipe_id=recipe.id,
                        product_id=product.id,
                        component_type=recipe_row.component_type,
                        amount=recipe_row.amount,
                        unit=recipe_row.unit,
                        calculation_type=recipe_row.calculation_type,
                        people_count=recipe_row.people_count,
                    )
                )

                if recipe_row.note_text and recipe_row.note_type:
                    note_key = (
                        recipe.id,
                        recipe_row.note_type,
                        recipe_row.note_text,
                        recipe_row.note_priority,
                    )
                    if note_key not in notes:
                        notes.add(note_key)
                        self.session.add(
                            RecipeNoteORM(
                                id=str(uuid4()),
                                recipe_id=recipe.id,
                                type=recipe_row.note_type,
                                text=recipe_row.note_text,
                                priority=recipe_row.note_priority,
                            )
                        )

            OperationalAuditService(self.session).record_catalog_import(
                actor=self.actor,
                result=result,
            )
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            raise

    def _preview_token(
        self,
        *,
        kind: CatalogImportKind,
        content: str,
        ownership_scope: RecipeImportOwnership,
    ) -> str:
        payload = "\0".join(
            (
                "tourhub-catalog-import-v1",
                str(self.actor.id),
                kind,
                ownership_scope,
                content,
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()
