from fastapi import APIRouter

from app.modules.api import equipment_list_router, recipe_equipment_router
from app.modules.api.appearance_settings_router import router as appearance_settings_router
from app.modules.api.catalog_import_router import router as catalog_import_router
from app.modules.api.club_settings_router import router as club_settings_router
from app.modules.api.dish_router import router as dish_router
from app.modules.api.document_appearance_settings_router import (
    router as document_appearance_settings_router,
)
from app.modules.api.invitation_settings_router import router as invitation_settings_router
from app.modules.api.mail_settings_router import router as mail_settings_router
from app.modules.api.meal_plan_router import router as meal_plan_router
from app.modules.api.meal_slot_router import router as meal_slot_router
from app.modules.api.meta_router import router as meta_router
from app.modules.api.module_settings_router import router as module_settings_router
from app.modules.api.product_router import router as product_router
from app.modules.api.project_preparation_status_router import router as preparation_status_router
from app.modules.api.purchase_checklist_router import router as purchase_checklist_router
from app.modules.api.purchase_dashboard_router import router as purchase_dashboard_router
from app.modules.api.purchase_list_router import router as purchase_list_router
from app.modules.api.recipe_note_router import router as recipe_note_router
from app.modules.api.recipe_router import router as recipe_router
from app.modules.api.system_settings_router import router as system_settings_router
from app.modules.projects.router import router as project_router

router = APIRouter(prefix="/api/v1")

router.include_router(appearance_settings_router)
router.include_router(catalog_import_router)
router.include_router(club_settings_router)
router.include_router(dish_router)
router.include_router(document_appearance_settings_router)
router.include_router(equipment_list_router.router)
router.include_router(invitation_settings_router)
router.include_router(mail_settings_router)
router.include_router(meal_plan_router)
router.include_router(meal_slot_router)
router.include_router(meta_router)
router.include_router(module_settings_router)
router.include_router(product_router)
router.include_router(project_router)
router.include_router(preparation_status_router)
router.include_router(purchase_checklist_router)
router.include_router(purchase_list_router)
router.include_router(purchase_dashboard_router)
router.include_router(recipe_router)
router.include_router(recipe_equipment_router.router)
router.include_router(recipe_note_router)
router.include_router(system_settings_router)


@router.get("/")
async def root() -> dict[str, str]:
    return {"name": "TourHub", "environment": "development", "status": "running"}


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
