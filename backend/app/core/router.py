from fastapi import APIRouter
from app.modules.api.meal_router import router as meal_router
from app.modules.api.meal_plan_router import router as meal_plan_router

router = APIRouter()


router.include_router(meal_router)
router.include_router(meal_plan_router)

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
