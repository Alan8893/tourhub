from pydantic import BaseModel, Field


class DishRecipeResponse(BaseModel):
    id: str
    name: str
    is_archived: bool


class DishResponse(BaseModel):
    id: str
    name: str
    recipe: DishRecipeResponse


class DishListResponse(BaseModel):
    items: list[DishResponse]


class DishCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    recipe_id: str = Field(min_length=1)


class DishUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    recipe_id: str = Field(min_length=1)
