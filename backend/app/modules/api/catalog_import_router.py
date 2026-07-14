from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.schemas.catalog_import import CatalogImportRequest, CatalogImportResult
from app.services.catalog_import_service import CatalogImportService

router = APIRouter(prefix="/catalog-import", tags=["Catalog import"])


@router.post("/preview", response_model=CatalogImportResult)
def preview_catalog_import(
    request: CatalogImportRequest,
    session: Session = Depends(get_session),
) -> CatalogImportResult:
    return CatalogImportService(session).preview(request.kind, request.content)


@router.post("/apply", response_model=CatalogImportResult)
def apply_catalog_import(
    request: CatalogImportRequest,
    session: Session = Depends(get_session),
) -> CatalogImportResult:
    return CatalogImportService(session).apply(request.kind, request.content)
