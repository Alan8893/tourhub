import { apiClient } from "@/shared/api/client";

export interface RecipeListItem {
  id: string;
  name: string;
  component_count: number;
  note_count: number;
}

export interface RecipeListResponse {
  items: RecipeListItem[];
}

export interface RecipeProduct {
  id: string;
  name: string;
  category: string | null;
  unit: string;
  package_size: number | null;
}

export interface ProductListResponse {
  items: RecipeProduct[];
}

export interface RecipeComponent {
  id: string;
  component_type: string;
  amount: number;
  unit: string;
  calculation_type: string;
  people_count: number | null;
  product: RecipeProduct;
}

export interface RecipeNote {
  id: string;
  type: string;
  text: string;
  priority: number;
  created_at: string;
}

export interface RecipeDetail {
  id: string;
  name: string;
  components: RecipeComponent[];
  notes: RecipeNote[];
}

export interface RecipeWriteResponse {
  id: string;
  name: string;
}

export interface RecipeComponentWriteInput {
  product_id: string;
  component_type: "base" | "cooking" | "optional" | "serving_add_on";
  amount: number;
  unit: string;
  calculation_type: "per_person" | "fixed_group" | "package_per_people";
  people_count: number | null;
}

export async function getRecipes(): Promise<RecipeListResponse> {
  const response = await apiClient.get<RecipeListResponse>("/recipes");
  return response.data;
}

export async function getRecipe(recipeId: string): Promise<RecipeDetail> {
  const response = await apiClient.get<RecipeDetail>(`/recipes/${recipeId}`);
  return response.data;
}

export async function getProducts(): Promise<ProductListResponse> {
  const response = await apiClient.get<ProductListResponse>("/products");
  return response.data;
}

export async function createRecipe(name: string): Promise<RecipeWriteResponse> {
  const response = await apiClient.post<RecipeWriteResponse>("/recipes", { name });
  return response.data;
}

export async function renameRecipe(recipeId: string, name: string): Promise<RecipeWriteResponse> {
  const response = await apiClient.patch<RecipeWriteResponse>(`/recipes/${recipeId}`, { name });
  return response.data;
}

export async function addRecipeComponent(
  recipeId: string,
  input: RecipeComponentWriteInput,
): Promise<RecipeComponent> {
  const response = await apiClient.post<RecipeComponent>(
    `/recipes/${recipeId}/components`,
    input,
  );
  return response.data;
}

export async function updateRecipeComponent(
  recipeId: string,
  componentId: string,
  input: RecipeComponentWriteInput,
): Promise<RecipeComponent> {
  const response = await apiClient.put<RecipeComponent>(
    `/recipes/${recipeId}/components/${componentId}`,
    input,
  );
  return response.data;
}

export async function deleteRecipeComponent(
  recipeId: string,
  componentId: string,
): Promise<void> {
  await apiClient.delete(`/recipes/${recipeId}/components/${componentId}`);
}
