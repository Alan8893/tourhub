from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.user import UserORM
from app.schemas.catalog_import import (
    CatalogImportApplyRequest,
    CatalogImportRequest,
    CatalogImportResult,
)
from app.services.ownership_aware_catalog_import_service import (
    OwnershipAwareCatalogImportService,
)

router = APIRouter(prefix="/catalog-import", tags=["Catalog import"])


@router.post("/preview", response_model=CatalogImportResult)
def preview_catalog_import(
    request: CatalogImportRequest,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> CatalogImportResult:
    return OwnershipAwareCatalogImportService(session, actor=actor).preview(
        request.kind,
        request.content,
        ownership_scope=request.ownership_scope,
    )


@router.post("/apply", response_model=CatalogImportResult)
def apply_catalog_import(
    request: CatalogImportApplyRequest,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> CatalogImportResult:
    return OwnershipAwareCatalogImportService(session, actor=actor).apply(
        request.kind,
        request.content,
        ownership_scope=request.ownership_scope,
        preview_token=request.preview_token,
    )
