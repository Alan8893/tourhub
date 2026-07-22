import { apiClient } from "@/shared/api/client";

import type { RecipeProduct } from "./recipeApi";

export interface ArchivedProduct extends RecipeProduct {
  is_archived: boolean;
  archived_by_alcohol_policy: boolean;
}

interface ProductArchiveListResponse {
  items: ArchivedProduct[];
}

export async function getArchivedProducts(): Promise<ProductArchiveListResponse> {
  const response = await apiClient.get<ProductArchiveListResponse>("/products/archive");
  return response.data;
}

export async function archiveProduct(productId: string): Promise<ArchivedProduct> {
  const response = await apiClient.post<ArchivedProduct>(`/products/${productId}/archive`);
  return response.data;
}

export async function restoreProduct(productId: string): Promise<ArchivedProduct> {
  const response = await apiClient.post<ArchivedProduct>(`/products/${productId}/restore`);
  return response.data;
}
