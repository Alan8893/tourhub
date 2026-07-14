from pydantic import BaseModel, Field


class RecipeNoteResponse(BaseModel):
    id: str
    recipe_id: str
    type: str
    text: str
    priority: int = Field(ge=0)
    created_at: str


class RecipeNoteListResponse(BaseModel):
    items: list[RecipeNoteResponse]
