from pydantic import BaseModel


class ProjectCreateRequest(BaseModel):
    name: str
    participants: int
    days: int
    start_date: str | None = None
    first_meal: str | None = None
    last_meal: str | None = None


class ProjectParticipantsUpdateRequest(BaseModel):
    participants: int


class ProjectResponse(BaseModel):
    id: int
    name: str
    participants: int
    days: int
    start_date: str | None
    first_meal: str | None
    last_meal: str | None
    status: str


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
