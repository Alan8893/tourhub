import { apiClient } from "@/shared/api/client";

export type RecipeScope = "club" | "personal";
export type RecipeLifecycleStatus = "draft" | "submitted" | "rejected" | "published";
export type RecipeView = "library" | "moderation";

export interface RecipeOwnership {
  scope: RecipeScope;
  owner_user_id: number | null;
  owner_display_name: string | null;
  is_owned_by_current_user: boolean;
  lifecycle_status: RecipeLifecycleStatus;
  submitted_by_user_id: number | null;
  submitted_by_display_name: string | null;
  submitted_at: string | null;
  reviewed_by_user_id: number | null;
  reviewed_by_display_name: string | null;
  reviewed_at: string | null;
  review_comment: string | null;
  can_edit: boolean;
  can_archive: boolean;
  can_restore: boolean;
  can_delete: boolean;
  can_submit: boolean;
  can_publish: boolean;
  can_reject: boolean;
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

function normalizeLegacyRecipeListItem(item: RecipeListItem): RecipeListItem {
  return {
    ...item,
    scope: item.scope ?? "club",
    owner_user_id: item.owner_user_id ?? null,
    owner_display_name: item.owner_display_name ?? null,
    is_owned_by_current_user: item.is_owned_by_current_user ?? false,
    lifecycle_status: item.lifecycle_status ?? "published",
    submitted_by_user_id: item.submitted_by_user_id ?? null,
    submitted_by_display_name: item.submitted_by_display_name ?? null,
    submitted_at: item.submitted_at ?? null,
    reviewed_by_user_id: item.reviewed_by_user_id ?? null,
    reviewed_by_display_name: item.reviewed_by_display_name ?? null,
    reviewed_at: item.reviewed_at ?? null,
    review_comment: item.review_comment ?? null,
    can_edit: item.can_edit ?? true,
    can_archive: item.can_archive ?? !item.is_archived,
    can_restore: item.can_restore ?? item.is_archived,
    can_delete: item.can_delete ?? true,
    can_submit: item.can_submit ?? false,
    can_publish: item.can_publish ?? false,
    can_reject: item.can_reject ?? false,
  };
}

export async function getRecipes(
  includeArchived = false,
  view: RecipeView = "library",
): Promise<RecipeListResponse> {
  const response = await apiClient.get<RecipeListResponse>("/recipes", {
    params: {
      ...(includeArchived ? { include_archived: true } : {}),
      ...(view === "moderation" ? { view } : {}),
    },
  });
  return { items: response.data.items.map(normalizeLegacyRecipeListItem) };
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

export async function updateProduct(
  productId: string,
  input: ProductWriteInput,
): Promise<RecipeProduct> {
  const response = await apiClient.put<RecipeProduct>(`/products/${productId}`, input);
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

export async function submitRecipe(recipeId: string): Promise<RecipeWriteResponse> {
  const response = await apiClient.post<RecipeWriteResponse>(`/recipes/${recipeId}/submit`);
  return response.data;
}

export async function publishRecipe(recipeId: string): Promise<RecipeWriteResponse> {
  const response = await apiClient.post<RecipeWriteResponse>(`/recipes/${recipeId}/publish`);
  return response.data;
}

export async function rejectRecipe(
  recipeId: string,
  comment: string,
): Promise<RecipeWriteResponse> {
  const response = await apiClient.post<RecipeWriteResponse>(`/recipes/${recipeId}/reject`, {
    comment,
  });
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
