from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.models.product import ProductORM
from app.policies.alcohol_policy import AlcoholPolicy, AlcoholPolicyViolation
from app.schemas.recipe import (
    ProductCreateRequest,
    ProductListResponse,
    ProductUpdateRequest,
    RecipeProductResponse,
)

router = APIRouter(prefix="/products", tags=["Products"])


def _response(product: ProductORM) -> RecipeProductResponse:
    return RecipeProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        unit=product.unit,
        package_size=product.package_size,
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


def _commit_product(session: Session, product: ProductORM) -> RecipeProductResponse:
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Product name already exists") from exc
    session.refresh(product)
    return _response(product)


@router.get("", response_model=ProductListResponse)
def list_products(session: Session = Depends(get_session)) -> ProductListResponse:
    products = session.scalars(
        select(ProductORM)
        .where(ProductORM.is_archived.is_(False))
        .order_by(ProductORM.name)
    ).all()
    return ProductListResponse(items=[_response(product) for product in products])


@router.post("", response_model=RecipeProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    request: ProductCreateRequest,
    session: Session = Depends(get_session),
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
    return _commit_product(session, product)


@router.put("/{product_id}", response_model=RecipeProductResponse)
def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    session: Session = Depends(get_session),
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
    product.name = name
    product.category = category
    product.unit = unit
    product.package_size = request.package_size
    return _commit_product(session, product)
