from typing import Literal

from pydantic import BaseModel, field_validator

from app.models.recipe_generation_mode import RecipeGenerationMode
from app.schemas.auth import UserRole


class ProjectCreateRequest(BaseModel):
    name: str
    participants: int
    days: int
    start_date: str | None = None
    first_meal: str | None = None
    last_meal: str | None = None
    recipe_generation_mode: RecipeGenerationMode = RecipeGenerationMode.CLUB_ONLY


class ProjectParticipantsUpdateRequest(BaseModel):
    participants: int


class ProjectRecipeGenerationModeUpdateRequest(BaseModel):
    recipe_generation_mode: RecipeGenerationMode


class ProjectStatusUpdateRequest(BaseModel):
    status: Literal["completed"]


class ProjectTeamUpdateRequest(BaseModel):
    instructor_user_ids: list[int]

    @field_validator("instructor_user_ids")
    @classmethod
    def validate_ids(cls, value: list[int]) -> list[int]:
        if any(user_id <= 0 for user_id in value):
            raise ValueError("Instructor IDs must be positive")
        if len(value) != len(set(value)):
            raise ValueError("Instructor IDs must be unique")
        return value


class ProjectOwnerTransferRequest(BaseModel):
    new_owner_user_id: int


class ProjectCapabilitiesResponse(BaseModel):
    can_view: bool
    can_manage_project: bool
    can_manage_team: bool
    can_transfer_ownership: bool
    can_edit_menu: bool
    can_operate_shopping: bool
    can_operate_equipment: bool
    can_generate_documents: bool
    can_delete: bool


class ProjectMemberResponse(BaseModel):
    id: int
    email: str
    display_name: str
    phone: str | None
    telegram_url: str | None
    max_url: str | None
    vk_url: str | None
    role: UserRole
    is_active: bool
    project_role: Literal["owner", "additional_instructor"]


class ProjectTeamCandidateResponse(BaseModel):
    id: int
    email: str
    display_name: str
    role: UserRole
    is_active: bool


class ProjectTeamResponse(BaseModel):
    owner: ProjectMemberResponse
    instructors: list[ProjectMemberResponse]


class ProjectResponse(BaseModel):
    id: int
    name: str
    participants: int
    days: int
    start_date: str | None
    first_meal: str | None
    last_meal: str | None
    recipe_generation_mode: RecipeGenerationMode
    status: str
    owner_user_id: int | None = None
    owner_display_name: str | None = None
    capabilities: ProjectCapabilitiesResponse | None = None


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
