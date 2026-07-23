import { apiClient } from "@/shared/api/client";

export type CatalogImportKind = "products" | "recipes";
export type RecipeImportOwnership = "club" | "personal";

export interface CatalogImportError {
  row: number;
  field: string | null;
  message: string;
}

export interface CatalogImportResult {
  kind: CatalogImportKind;
  valid: boolean;
  row_count: number;
  create_count: number;
  skip_count: number;
  component_count: number;
  note_count: number;
  ownership_scope: RecipeImportOwnership | null;
  preview_token: string | null;
  errors: CatalogImportError[];
}

export interface CatalogImportRequest {
  kind: CatalogImportKind;
  content: string;
  ownership_scope?: RecipeImportOwnership;
  preview_token?: string;
}

export async function previewCatalogImport(
  request: CatalogImportRequest,
): Promise<CatalogImportResult> {
  const response = await apiClient.post<CatalogImportResult>("/catalog-import/preview", request);
  return response.data;
}

export async function applyCatalogImport(
  request: CatalogImportRequest,
): Promise<CatalogImportResult> {
  const response = await apiClient.post<CatalogImportResult>("/catalog-import/apply", request);
  return response.data;
}
