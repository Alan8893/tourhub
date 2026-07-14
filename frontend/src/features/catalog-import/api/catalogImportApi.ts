import { apiClient } from "@/shared/api/client";

export type CatalogImportKind = "products" | "recipes";

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
  errors: CatalogImportError[];
}

interface CatalogImportRequest {
  kind: CatalogImportKind;
  content: string;
}

export async function previewCatalogImport(
  input: CatalogImportRequest,
): Promise<CatalogImportResult> {
  const response = await apiClient.post<CatalogImportResult>(
    "/catalog-import/preview",
    input,
  );
  return response.data;
}

export async function applyCatalogImport(
  input: CatalogImportRequest,
): Promise<CatalogImportResult> {
  const response = await apiClient.post<CatalogImportResult>(
    "/catalog-import/apply",
    input,
  );
  return response.data;
}
