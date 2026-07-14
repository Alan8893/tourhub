from pydantic import BaseModel, Field


class RecipeNoteCreateRequest(BaseModel):
    type: str = Field(default="cooking_tip")
    text: str = Field(min_length=1)
    priority: int = Field(default=100, ge=0)


class RecipeNoteResponse(BaseModel):
    id: str
    recipe_id: str
    type: str
    text: str
    priority: int = Field(ge=0)
    created_at: str


class RecipeNoteListResponse(BaseModel):
    items: list[RecipeNoteResponse]
