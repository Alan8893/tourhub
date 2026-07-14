from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.models.product import ProductORM
from app.schemas.recipe import ProductListResponse, RecipeProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=ProductListResponse)
def list_products(session: Session = Depends(get_session)) -> ProductListResponse:
    products = session.scalars(select(ProductORM).order_by(ProductORM.name)).all()
    return ProductListResponse(
        items=[
            RecipeProductResponse(
                id=product.id,
                name=product.name,
                category=product.category,
                unit=product.unit,
                package_size=product.package_size,
            )
            for product in products
        ]
    )
