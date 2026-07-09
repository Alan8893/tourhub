from pydantic import BaseModel


class ProjectCreateRequest(BaseModel):
    name: str
    participants: int
    days: int
    start_date: str | None = None
    first_meal: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    participants: int
    days: int
    start_date: str | None
    first_meal: str | None
    status: str
