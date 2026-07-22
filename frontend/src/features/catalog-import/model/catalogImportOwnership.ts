import type {
  CatalogImportKind,
  CatalogImportRequest,
  CatalogImportResult,
  RecipeImportOwnership,
} from "../api/catalogImportApi";

export function recipeImportOwnershipLabel(scope: RecipeImportOwnership): string {
  return scope === "personal" ? "Личные рецепты" : "Клубные рецепты";
}

export function recipeImportOwnershipDescription(scope: RecipeImportOwnership): string {
  return scope === "personal"
    ? "Рецепты будут созданы как ваши личные черновики. Их можно отправить на модерацию позднее."
    : "Рецепты будут сразу созданы в клубной библиотеке со статусом опубликованных.";
}

export function buildCatalogImportPreviewRequest(
  kind: CatalogImportKind,
  content: string,
  ownershipScope: RecipeImportOwnership,
): CatalogImportRequest {
  return kind === "recipes"
    ? { kind, content, ownership_scope: ownershipScope }
    : { kind, content };
}

export function buildCatalogImportApplyRequest(
  kind: CatalogImportKind,
  content: string,
  ownershipScope: RecipeImportOwnership,
  preview: CatalogImportResult,
): CatalogImportRequest {
  if (kind === "products") return { kind, content };
  if (
    preview.ownership_scope !== ownershipScope ||
    !preview.preview_token
  ) {
    throw new Error("Recipe import preview no longer matches the selected ownership scope");
  }
  return {
    kind,
    content,
    ownership_scope: ownershipScope,
    preview_token: preview.preview_token,
  };
}
