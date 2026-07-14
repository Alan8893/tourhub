from pydantic import BaseModel, Field

from app.models.recipe_note_type import RecipeNoteType


class RecipeNoteWriteRequest(BaseModel):
    type: RecipeNoteType = RecipeNoteType.COOKING_TIP
    text: str = Field(min_length=1, max_length=4000)
    priority: int = Field(default=100, ge=0)


class RecipeNoteCreateRequest(RecipeNoteWriteRequest):
    pass


class RecipeNoteResponse(BaseModel):
    id: str
    recipe_id: str
    type: str
    text: str
    priority: int = Field(ge=0)
    created_at: str


class RecipeNoteListResponse(BaseModel):
    items: list[RecipeNoteResponse]
