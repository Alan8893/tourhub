import { apiClient } from "@/shared/api/client";

export type RecipeScope = "club" | "personal";

export interface RecipeOwnership {
  scope: RecipeScope;
  owner_user_id: number | null;
  owner_display_name: string | null;
  is_owned_by_current_user: boolean;
  can_edit: boolean;
  can_archive: boolean;
  can_restore: boolean;
  can_delete: boolean;
}

export interface RecipeListItem extends RecipeOwnership {
  id: string;
  name: string;
  component_count: number;
  note_count: number;
  is_archived: boolean;
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

export interface ProductWriteInput {
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

export interface RecipeNoteWriteInput {
  type: "cooking_tip" | "expedition_tip" | "serving_tip";
  text: string;
  priority: number;
}

export interface RecipeDetail extends RecipeOwnership {
  id: string;
  name: string;
  is_archived: boolean;
  components: RecipeComponent[];
  notes: RecipeNote[];
}

export interface RecipeWriteResponse extends RecipeOwnership {
  id: string;
  name: string;
  is_archived: boolean;
}

export interface RecipeComponentWriteInput {
  product_id: string;
  component_type: "base" | "cooking" | "optional" | "serving_add_on";
  amount: number;
  unit: string;
  calculation_type: "per_person" | "fixed_group" | "package_per_people";
  people_count: number | null;
}

export async function getRecipes(includeArchived = false): Promise<RecipeListResponse> {
  const response = await apiClient.get<RecipeListResponse>("/recipes", {
    params: includeArchived ? { include_archived: true } : undefined,
  });
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

export async function createProduct(input: ProductWriteInput): Promise<RecipeProduct> {
  const response = await apiClient.post<RecipeProduct>("/products", input);
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

export async function archiveRecipe(recipeId: string): Promise<RecipeWriteResponse> {
  const response = await apiClient.post<RecipeWriteResponse>(`/recipes/${recipeId}/archive`);
  return response.data;
}

export async function restoreRecipe(recipeId: string): Promise<RecipeWriteResponse> {
  const response = await apiClient.post<RecipeWriteResponse>(`/recipes/${recipeId}/restore`);
  return response.data;
}

export async function deleteRecipe(recipeId: string): Promise<void> {
  await apiClient.delete(`/recipes/${recipeId}`);
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

export async function createRecipeNote(
  recipeId: string,
  input: RecipeNoteWriteInput,
): Promise<RecipeNote> {
  const response = await apiClient.post<RecipeNote>(`/recipes/${recipeId}/notes`, input);
  return response.data;
}

export async function updateRecipeNote(
  recipeId: string,
  noteId: string,
  input: RecipeNoteWriteInput,
): Promise<RecipeNote> {
  const response = await apiClient.put<RecipeNote>(
    `/recipes/${recipeId}/notes/${noteId}`,
    input,
  );
  return response.data;
}

export async function deleteRecipeNote(recipeId: string, noteId: string): Promise<void> {
  await apiClient.delete(`/recipes/${recipeId}/notes/${noteId}`);
}
