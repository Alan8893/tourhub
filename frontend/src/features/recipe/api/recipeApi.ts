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

export async function getRecipes(): Promise<RecipeListResponse> {
  const response = await apiClient.get<RecipeListResponse>("/recipes");
  return response.data;
}

export async function getRecipe(recipeId: string): Promise<RecipeDetail> {
  const response = await apiClient.get<RecipeDetail>(`/recipes/${recipeId}`);
  return response.data;
}
