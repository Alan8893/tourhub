from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.user import UserORM
from app.schemas.catalog_import import CatalogImportRequest, CatalogImportResult
from app.services.alcohol_catalog_import_service import (
    AlcoholAwareCatalogImportService,
)

router = APIRouter(prefix="/catalog-import", tags=["Catalog import"])


@router.post("/preview", response_model=CatalogImportResult)
def preview_catalog_import(
    request: CatalogImportRequest,
    session: Session = Depends(get_session),
) -> CatalogImportResult:
    return AlcoholAwareCatalogImportService(session).preview(
        request.kind,
        request.content,
    )


@router.post("/apply", response_model=CatalogImportResult)
def apply_catalog_import(
    request: CatalogImportRequest,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> CatalogImportResult:
    return AlcoholAwareCatalogImportService(session, actor=actor).apply(
        request.kind,
        request.content,
    )
