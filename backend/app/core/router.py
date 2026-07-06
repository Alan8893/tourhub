from fastapi import APIRouter
from app.modules.api.meal_router import router as meal_router

router = APIRouter()


router.include_router(meal_router)

@router.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "TourHub",
        "environment": "development",
        "status": "running",
    }


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }