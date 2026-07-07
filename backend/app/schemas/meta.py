from pydantic import BaseModel


class WorkflowStatusesResponse(BaseModel):
    purchase_list: list[str]
    purchase_checklist: list[str]


class MetaResponse(BaseModel):
    name: str
    version: str
    api_version: str
    statuses: WorkflowStatusesResponse
