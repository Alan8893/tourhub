from pydantic import BaseModel, Field

from app.models.recipe_scope import RecipeScope
from app.modules.domain.meal_role import MealRole
from app.modules.domain.meal_type import MealType


class DishRecipeResponse(BaseModel):
    id: str
    name: str
    is_archived: bool
    scope: RecipeScope
    owner_display_name: str | None = None
    is_default: bool = False


class DishMealRoleResponse(BaseModel):
    role: MealRole
    is_repeatable: bool
    allowed_meal_types: list[MealType]


class DishResponse(BaseModel):
    id: str
    name: str
    recipe: DishRecipeResponse
    recipes: list[DishRecipeResponse] = Field(default_factory=list)
    meal_roles: list[DishMealRoleResponse] = Field(default_factory=list)


class DishListResponse(BaseModel):
    items: list[DishResponse]


class DishCatalogueCoverageResponse(BaseModel):
    meal_type: MealType
    role: MealRole
    required: bool
    candidate_count: int
    minimum_required: int
    ready: bool


class DishCatalogueReadinessResponse(BaseModel):
    ready: bool
    active_dish_count: int
    classified_dish_count: int
    unclassified_dish_count: int
    coverage: list[DishCatalogueCoverageResponse]


class DishCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    recipe_id: str = Field(min_length=1)
    recipe_ids: list[str] = Field(default_factory=list)


class DishUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    recipe_id: str = Field(min_length=1)
    recipe_ids: list[str] = Field(default_factory=list)


class DishMealRoleRequest(BaseModel):
    role: MealRole
    is_repeatable: bool = False
    allowed_meal_types: list[MealType] = Field(min_length=1)


class DishMealRolesUpdateRequest(BaseModel):
    roles: list[DishMealRoleRequest]
