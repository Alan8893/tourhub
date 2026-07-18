import { apiClient } from "@/shared/api/client";

export type MealRole = "main" | "addition" | "drink" | "snack";
export type MealType = "breakfast" | "snack" | "lunch" | "dinner";
export type DishRecipeScope = "club" | "personal";

export interface DishMealRole {
  role: MealRole;
  is_repeatable: boolean;
  allowed_meal_types: MealType[];
}

export interface DishRecipe {
  id: string;
  name: string;
  is_archived: boolean;
  scope: DishRecipeScope;
  owner_display_name: string | null;
  is_default: boolean;
}

export interface Dish {
  id: string;
  name: string;
  recipe: DishRecipe;
  recipes: DishRecipe[];
  meal_roles: DishMealRole[];
}

export interface DishListResponse {
  items: Dish[];
}

export interface DishCatalogueCoverage {
  meal_type: MealType;
  role: MealRole;
  required: boolean;
  candidate_count: number;
  minimum_required: number;
  ready: boolean;
}

export interface DishCatalogueReadiness {
  ready: boolean;
  active_dish_count: number;
  classified_dish_count: number;
  unclassified_dish_count: number;
  coverage: DishCatalogueCoverage[];
}

export interface DishWriteInput {
  name: string;
  recipe_id: string;
  recipe_ids?: string[];
}

export interface DishMealRoleWriteInput {
  role: MealRole;
  is_repeatable: boolean;
  allowed_meal_types: MealType[];
}

export interface DishMealRolesWriteInput {
  roles: DishMealRoleWriteInput[];
}

type LegacyDishRecipe = Partial<DishRecipe> & Pick<DishRecipe, "id" | "name" | "is_archived">;
type LegacyDish = Omit<Dish, "recipe" | "recipes"> & {
  recipe: LegacyDishRecipe;
  recipes?: LegacyDishRecipe[];
};

function normalizeRecipe(recipe: LegacyDishRecipe, defaultRecipeId: string): DishRecipe {
  return {
    ...recipe,
    scope: recipe.scope ?? "club",
    owner_display_name: recipe.owner_display_name ?? null,
    is_default: recipe.is_default ?? recipe.id === defaultRecipeId,
  };
}

function normalizeDish(dish: LegacyDish): Dish {
  const defaultRecipe = normalizeRecipe(dish.recipe, dish.recipe.id);
  const recipes = (dish.recipes?.length ? dish.recipes : [dish.recipe]).map((recipe) =>
    normalizeRecipe(recipe, defaultRecipe.id),
  );
  return {
    ...dish,
    recipe: defaultRecipe,
    recipes,
  };
}

export async function getDishes(): Promise<DishListResponse> {
  const response = await apiClient.get<{ items: LegacyDish[] }>("/dishes");
  return { items: response.data.items.map(normalizeDish) };
}

export async function getDishCatalogueReadiness(): Promise<DishCatalogueReadiness> {
  const response = await apiClient.get<DishCatalogueReadiness>("/dishes/catalogue-readiness");
  return response.data;
}

export async function getDish(dishId: string): Promise<Dish> {
  const response = await apiClient.get<LegacyDish>(`/dishes/${dishId}`);
  return normalizeDish(response.data);
}

export async function createDish(input: DishWriteInput): Promise<Dish> {
  const response = await apiClient.post<LegacyDish>("/dishes", input);
  return normalizeDish(response.data);
}

export async function updateDish(dishId: string, input: DishWriteInput): Promise<Dish> {
  const response = await apiClient.put<LegacyDish>(`/dishes/${dishId}`, input);
  return normalizeDish(response.data);
}

export async function updateDishMealRoles(
  dishId: string,
  input: DishMealRolesWriteInput,
): Promise<Dish> {
  const response = await apiClient.put<LegacyDish>(`/dishes/${dishId}/meal-roles`, input);
  return normalizeDish(response.data);
}
