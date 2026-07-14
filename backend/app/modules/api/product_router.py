from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.models.product import ProductORM
from app.schemas.recipe import (
    ProductCreateRequest,
    ProductListResponse,
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


@router.get("", response_model=ProductListResponse)
def list_products(session: Session = Depends(get_session)) -> ProductListResponse:
    products = session.scalars(select(ProductORM).order_by(ProductORM.name)).all()
    return ProductListResponse(items=[_response(product) for product in products])


@router.post("", response_model=RecipeProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    request: ProductCreateRequest,
    session: Session = Depends(get_session),
) -> RecipeProductResponse:
    product = ProductORM(
        id=str(uuid4()),
        name=request.name.strip(),
        category=request.category.strip() if request.category else None,
        unit=request.unit.strip(),
        package_size=request.package_size,
    )
    session.add(product)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Product name already exists") from exc
    session.refresh(product)
    return _response(product)
