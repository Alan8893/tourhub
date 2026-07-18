from pydantic import BaseModel

from app.models.recipe_generation_mode import RecipeGenerationMode


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


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
