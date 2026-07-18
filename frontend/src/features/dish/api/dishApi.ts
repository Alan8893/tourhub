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

export async function getDishes(): Promise<DishListResponse> {
  const response = await apiClient.get<DishListResponse>("/dishes");
  return response.data;
}

export async function getDishCatalogueReadiness(): Promise<DishCatalogueReadiness> {
  const response = await apiClient.get<DishCatalogueReadiness>("/dishes/catalogue-readiness");
  return response.data;
}

export async function getDish(dishId: string): Promise<Dish> {
  const response = await apiClient.get<Dish>(`/dishes/${dishId}`);
  return response.data;
}

export async function createDish(input: DishWriteInput): Promise<Dish> {
  const response = await apiClient.post<Dish>("/dishes", input);
  return response.data;
}

export async function updateDish(dishId: string, input: DishWriteInput): Promise<Dish> {
  const response = await apiClient.put<Dish>(`/dishes/${dishId}`, input);
  return response.data;
}

export async function updateDishMealRoles(
  dishId: string,
  input: DishMealRolesWriteInput,
): Promise<Dish> {
  const response = await apiClient.put<Dish>(`/dishes/${dishId}/meal-roles`, input);
  return response.data;
}
