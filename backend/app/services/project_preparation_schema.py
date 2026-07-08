from pydantic import BaseModel


class ProjectPreparationResponse(BaseModel):
    project_id: int
    meal_plan_id: str
    purchase_list_id: str
    purchase_checklist_id: str
