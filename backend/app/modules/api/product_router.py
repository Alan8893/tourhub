from collections.abc import Mapping
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.product import ProductORM
from app.models.user import UserORM
from app.policies.alcohol_policy import AlcoholPolicy, AlcoholPolicyViolation
from app.schemas.recipe import (
    ProductCreateRequest,
    ProductListResponse,
    ProductUpdateRequest,
    RecipeProductResponse,
)
from app.services.operational_audit_service import OperationalAuditService
from app.services.product_archive_service import (
    ProductArchiveNotFoundError,
    ProductArchiveService,
    ProductRestoreBlockedError,
)

router = APIRouter(prefix="/products", tags=["Products"])


def _response(product: ProductORM) -> RecipeProductResponse:
    return RecipeProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        unit=product.unit,
        package_size=product.package_size,
        is_archived=product.is_archived,
        archived_by_alcohol_policy=product.archived_by_alcohol_policy,
    )


def _normalized_values(request: ProductCreateRequest) -> tuple[str, str | None, str]:
    name = request.name.strip()
    category = request.category.strip() if request.category else None
    unit = request.unit.strip()
    try:
        AlcoholPolicy.require_product_allowed(name=name, category=category)
    except AlcoholPolicyViolation as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return name, category, unit


def _commit_product(
    session: Session,
    product: ProductORM,
    *,
    actor: UserORM,
    before: Mapping[str, object] | None = None,
) -> RecipeProductResponse:
    audit = OperationalAuditService(session)
    if before is None:
        audit.record_product_created(actor=actor, product=product)
    else:
        audit.record_product_updated(actor=actor, product=product, before=before)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Product name already exists") from exc
    except Exception:
        session.rollback()
        raise
    session.refresh(product)
    return _response(product)


def _archive_service_response(
    operation: str,
    product_id: str,
    *,
    session: Session,
    actor: UserORM,
) -> RecipeProductResponse:
    service = ProductArchiveService(session, actor=actor)
    try:
        product = service.archive(product_id) if operation == "archive" else service.restore(product_id)
    except ProductArchiveNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ProductRestoreBlockedError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return _response(product)


@router.get("", response_model=ProductListResponse)
def list_products(session: Session = Depends(get_session)) -> ProductListResponse:
    products = session.scalars(
        select(ProductORM)
        .where(ProductORM.is_archived.is_(False))
        .order_by(ProductORM.name)
    ).all()
    return ProductListResponse(items=[_response(product) for product in products])


@router.get("/archive", response_model=ProductListResponse)
def list_archived_products(
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> ProductListResponse:
    del actor
    products = session.scalars(
        select(ProductORM)
        .where(ProductORM.is_archived.is_(True))
        .order_by(ProductORM.name)
    ).all()
    return ProductListResponse(items=[_response(product) for product in products])


@router.post("", response_model=RecipeProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    request: ProductCreateRequest,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> RecipeProductResponse:
    name, category, unit = _normalized_values(request)
    product = ProductORM(
        id=str(uuid4()),
        name=name,
        category=category,
        unit=unit,
        package_size=request.package_size,
    )
    session.add(product)
    return _commit_product(session, product, actor=actor)


@router.put("/{product_id}", response_model=RecipeProductResponse)
def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> RecipeProductResponse:
    product = session.scalar(
        select(ProductORM).where(
            ProductORM.id == product_id,
            ProductORM.is_archived.is_(False),
        )
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    name, category, unit = _normalized_values(request)
    audit = OperationalAuditService(session)
    before = audit.product_snapshot(product)
    product.name = name
    product.category = category
    product.unit = unit
    product.package_size = request.package_size
    if before == audit.product_snapshot(product):
        return _response(product)
    return _commit_product(session, product, actor=actor, before=before)


@router.post("/{product_id}/archive", response_model=RecipeProductResponse)
def archive_product(
    product_id: str,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> RecipeProductResponse:
    return _archive_service_response(
        "archive",
        product_id,
        session=session,
        actor=actor,
    )


@router.post("/{product_id}/restore", response_model=RecipeProductResponse)
def restore_product(
    product_id: str,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> RecipeProductResponse:
    return _archive_service_response(
        "restore",
        product_id,
        session=session,
        actor=actor,
    )
