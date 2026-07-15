from pydantic import BaseModel, Field

from app.modules.domain.meal_role import MealRole


class DishRecipeResponse(BaseModel):
    id: str
    name: str
    is_archived: bool


class DishMealRoleResponse(BaseModel):
    role: MealRole
    is_repeatable: bool


class DishResponse(BaseModel):
    id: str
    name: str
    recipe: DishRecipeResponse
    meal_roles: list[DishMealRoleResponse] = Field(default_factory=list)


class DishListResponse(BaseModel):
    items: list[DishResponse]


class DishCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    recipe_id: str = Field(min_length=1)


class DishUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    recipe_id: str = Field(min_length=1)


class DishMealRoleRequest(BaseModel):
    role: MealRole
    is_repeatable: bool = False


class DishMealRolesUpdateRequest(BaseModel):
    roles: list[DishMealRoleRequest]
