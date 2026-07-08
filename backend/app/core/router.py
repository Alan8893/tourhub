from fastapi import APIRouter

from app.modules.api.meal_router import router as meal_router
from app.modules.api.meal_plan_router import router as meal_plan_router
from app.modules.api.meta_router import router as meta_router
from app.modules.api.purchase_checklist_router import router as purchase_checklist_router
from app.modules.api.purchase_dashboard_router import router as purchase_dashboard_router
from app.modules.api.purchase_list_router import router as purchase_list_router
from app.modules.projects.router import router as project_router


router = APIRouter(prefix="/api/v1")


router.include_router(meal_router)
router.include_router(meal_plan_router)
router.include_router(meta_router)
router.include_router(purchase_checklist_router)
router.include_router(purchase_list_router)
router.include_router(purchase_dashboard_router)
router.include_router(project_router)


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
