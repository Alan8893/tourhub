import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Paper,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import { isAxiosError } from "axios";
import { useEffect, useState } from "react";

import type { ArchivedProduct } from "../api/productArchiveApi";
import type { RecipeProduct } from "../api/recipeApi";
import {
  useArchiveProduct,
  useArchivedProducts,
  useRestoreProduct,
} from "../hooks/useProductArchive";
import { useRecipeProducts } from "../hooks/useRecipes";
import {
  canRestoreArchivedProduct,
  productArchiveNotice,
} from "../model/productArchive";

interface ProductArchiveDialogProps {
  open: boolean;
  onClose: () => void;
}

type ProductArchiveView = "active" | "archived";

function getErrorMessage(error: unknown): string {
  if (isAxiosError<{ error?: string; detail?: string }>(error)) {
    const message = error.response?.data?.error ?? error.response?.data?.detail;
    if (
      message ===
      "Product cannot be restored because it is blocked by the central alcohol policy"
    ) {
      return "Продукт нельзя восстановить: центральная политика запрещает алкогольные позиции.";
    }
    return message ?? "Не удалось изменить состояние продукта.";
  }
  return error instanceof Error ? error.message : "Не удалось изменить состояние продукта.";
}

function productMeta(product: RecipeProduct): string {
  const parts = [product.category ?? "Без категории", product.unit];
  if (product.package_size) parts.push(`упаковка ${product.package_size}`);
  return parts.join(" · ");
}

function isArchivedProduct(
  product: RecipeProduct | ArchivedProduct,
): product is ArchivedProduct {
  return "archived_by_alcohol_policy" in product;
}

export default function ProductArchiveDialog({ open, onClose }: ProductArchiveDialogProps) {
  const [view, setView] = useState<ProductArchiveView>("active");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const activeQuery = useRecipeProducts(open);
  const archivedQuery = useArchivedProducts(open);
  const archiveMutation = useArchiveProduct();
  const restoreMutation = useRestoreProduct();
  const isMutating = archiveMutation.isPending || restoreMutation.isPending;

  useEffect(() => {
    if (open) {
      setView("active");
      setMessage(null);
      setError(null);
    }
  }, [open]);

  const archive = async (product: RecipeProduct) => {
    if (!window.confirm(`Архивировать продукт «${product.name}»?`)) return;
    setMessage(null);
    setError(null);
    try {
      await archiveMutation.mutateAsync(product.id);
      setMessage(`Продукт «${product.name}» перемещён в архив.`);
    } catch (mutationError) {
      setError(getErrorMessage(mutationError));
    }
  };

  const restore = async (productId: string, productName: string) => {
    setMessage(null);
    setError(null);
    try {
      await restoreMutation.mutateAsync(productId);
      setMessage(`Продукт «${productName}» восстановлен.`);
    } catch (mutationError) {
      setError(getErrorMessage(mutationError));
    }
  };

  const query = view === "active" ? activeQuery : archivedQuery;
  const products = query.data?.items ?? [];

  return (
    <Dialog open={open} onClose={isMutating ? undefined : onClose} fullWidth maxWidth="md">
      <DialogTitle>Архив продуктов</DialogTitle>
      <DialogContent>
        <Stack spacing={2.5} sx={{ mt: 1, minWidth: 0 }}>
          <Alert severity="info">
            Архивирование скрывает продукт из выбора для новых компонентов, но сохраняет его в
            существующих рецептах, закупках и документах.
          </Alert>
          <ToggleButtonGroup
            exclusive
            size="small"
            value={view}
            onChange={(_, next: ProductArchiveView | null) => {
              if (!next) return;
              setView(next);
              setMessage(null);
              setError(null);
            }}
            sx={{ alignSelf: "flex-start" }}
          >
            <ToggleButton value="active">Активные</ToggleButton>
            <ToggleButton value="archived">Архив</ToggleButton>
          </ToggleButtonGroup>

          {error && <Alert severity="error">{error}</Alert>}
          {message && <Alert severity="success">{message}</Alert>}

          {query.isLoading && (
            <Box sx={{ minHeight: 160, display: "grid", placeItems: "center" }}>
              <CircularProgress aria-label="Загрузка каталога продуктов" />
            </Box>
          )}
          {query.isError && (
            <Alert severity="error">
              {view === "active"
                ? "Не удалось загрузить активные продукты."
                : "Не удалось загрузить архив продуктов."}
            </Alert>
          )}
          {!query.isLoading && !query.isError && products.length === 0 && (
            <Alert severity="info">
              {view === "active" ? "Активных продуктов пока нет." : "Архив продуктов пуст."}
            </Alert>
          )}

          {!query.isLoading && !query.isError && products.length > 0 && (
            <Stack spacing={1.5}>
              {products.map((product) => {
                const archivedProduct = isArchivedProduct(product) ? product : null;
                const notice = archivedProduct ? productArchiveNotice(archivedProduct) : null;
                const canRestore = archivedProduct
                  ? canRestoreArchivedProduct(archivedProduct)
                  : false;
                return (
                  <Paper key={product.id} variant="outlined" sx={{ p: 2, minWidth: 0 }}>
                    <Stack
                      direction={{ xs: "column", sm: "row" }}
                      spacing={2}
                      justifyContent="space-between"
                      alignItems={{ xs: "stretch", sm: "center" }}
                    >
                      <Stack spacing={0.5} sx={{ minWidth: 0 }}>
                        <Stack
                          direction="row"
                          spacing={1}
                          alignItems="center"
                          flexWrap="wrap"
                          useFlexGap
                        >
                          <Typography fontWeight={600}>{product.name}</Typography>
                          {archivedProduct?.archived_by_alcohol_policy && (
                            <Chip
                              size="small"
                              color="warning"
                              label="Заблокирован политикой"
                            />
                          )}
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                          {productMeta(product)}
                        </Typography>
                        {notice && (
                          <Typography variant="body2" color="warning.main">
                            {notice}
                          </Typography>
                        )}
                      </Stack>
                      {view === "active" ? (
                        <Button
                          color="warning"
                          variant="outlined"
                          disabled={isMutating}
                          onClick={() => void archive(product)}
                          sx={{ flexShrink: 0 }}
                        >
                          {archiveMutation.isPending ? "Архивирование…" : "Архивировать"}
                        </Button>
                      ) : (
                        <Button
                          variant="contained"
                          disabled={!canRestore || isMutating}
                          onClick={() => void restore(product.id, product.name)}
                          sx={{ flexShrink: 0 }}
                        >
                          {restoreMutation.isPending ? "Восстановление…" : "Восстановить"}
                        </Button>
                      )}
                    </Stack>
                  </Paper>
                );
              })}
            </Stack>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isMutating}>Закрыть</Button>
      </DialogActions>
    </Dialog>
  );
}
