from pydantic import BaseModel


class ProjectCreateRequest(BaseModel):
    name: str
    participants: int
    days: int


class ProjectResponse(BaseModel):
    id: int
    name: str
    participants: int
    days: int
    status: str
