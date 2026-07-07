from pydantic import BaseModel


class PurchaseDashboardDocumentResponse(BaseModel):
    pdf_available: bool
    excel_available: bool


class PurchaseDashboardPurchaseListResponse(BaseModel):
    id: str | None
    status: str | None
    items_total: int
    packages_total: int


class PurchaseDashboardChecklistResponse(BaseModel):
    id: str | None
    status: str | None
    total_items: int
    checked_items: int
    progress_percent: float


class PurchaseDashboardResponse(BaseModel):
    meal_plan_id: str
    purchase_list: PurchaseDashboardPurchaseListResponse
    checklist: PurchaseDashboardChecklistResponse
    documents: PurchaseDashboardDocumentResponse
