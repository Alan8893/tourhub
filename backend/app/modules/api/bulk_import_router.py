from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.schemas.bulk_import import BulkCsvImportRequest, BulkImportResponse
from app.services.bulk_import_service import BulkImportService

router = APIRouter(prefix="/imports", tags=["Imports"])


@router.post("/products", response_model=BulkImportResponse)
def import_products(
    request: BulkCsvImportRequest,
    session: Session = Depends(get_session),
) -> BulkImportResponse:
    return BulkImportService(session).import_products(
        request.content,
        request.delimiter,
        dry_run=request.dry_run,
        skip_existing=request.skip_existing,
    )


@router.post("/recipes", response_model=BulkImportResponse)
def import_recipes(
    request: BulkCsvImportRequest,
    session: Session = Depends(get_session),
) -> BulkImportResponse:
    return BulkImportService(session).import_recipes(
        request.content,
        request.delimiter,
        dry_run=request.dry_run,
        skip_existing=request.skip_existing,
    )
