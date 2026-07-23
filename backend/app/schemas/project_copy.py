from pydantic import BaseModel, Field, model_validator

from app.models.recipe_generation_mode import RecipeGenerationMode


class ProjectCopyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    participants: int = Field(gt=0)
    days: int = Field(gt=0)
    start_date: str | None = Field(default=None, max_length=20)
    first_meal: str | None = Field(default=None, max_length=20)
    last_meal: str | None = Field(default=None, max_length=20)
    recipe_generation_mode: RecipeGenerationMode = RecipeGenerationMode.CLUB_ONLY

    @model_validator(mode="after")
    def validate_meal_boundaries(self) -> "ProjectCopyRequest":
        if (self.first_meal is None) != (self.last_meal is None):
            raise ValueError("First and last meal must be provided together")
        return self


class ProjectCopyResponse(BaseModel):
    project_id: int
    meal_plan_id: str
    copied_slot_count: int = Field(ge=0)
    copied_assignment_count: int = Field(ge=0)
    skipped_assignment_count: int = Field(ge=0)
    warnings: list[str]
