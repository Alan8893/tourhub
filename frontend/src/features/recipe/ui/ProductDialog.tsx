import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";

import type { RecipeProduct } from "../api/recipeApi";
import {
  toProductWriteInput,
  validateProductDraft,
  type ProductDraft,
} from "../model/recipeNotesProducts";

const initialDraft: ProductDraft = {
  name: "",
  category: "",
  unit: "gram",
  packageSize: "",
};

function draftFromProduct(product: RecipeProduct | null): ProductDraft {
  if (!product) return initialDraft;
  return {
    name: product.name,
    category: product.category ?? "",
    unit: product.unit,
    packageSize: product.package_size ? String(product.package_size) : "",
  };
}

interface ProductDialogProps {
  open: boolean;
  product: RecipeProduct | null;
  isSubmitting: boolean;
  errorMessage: string | null;
  onClose: () => void;
  onSubmit: (input: ReturnType<typeof toProductWriteInput>) => void;
}

export default function ProductDialog({
  open,
  product,
  isSubmitting,
  errorMessage,
  onClose,
  onSubmit,
}: ProductDialogProps) {
  const [draft, setDraft] = useState<ProductDraft>(initialDraft);
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setDraft(draftFromProduct(product));
      setValidationError(null);
    }
  }, [open, product]);

  const handleSubmit = () => {
    const error = validateProductDraft(draft);
    setValidationError(error);
    if (!error) {
      onSubmit(toProductWriteInput(draft));
    }
  };

  return (
    <Dialog open={open} onClose={isSubmitting ? undefined : onClose} fullWidth maxWidth="sm">
      <DialogTitle>{product ? "Изменить продукт" : "Новый продукт"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          {product && (
            <Alert severity="warning">
              Изменения будут видны во всех рецептах с этим продуктом. Количество и единица
              конкретных компонентов рецепта автоматически не пересчитываются.
            </Alert>
          )}
          {(validationError || errorMessage) && (
            <Alert severity="error">{validationError ?? errorMessage}</Alert>
          )}
          <TextField
            autoFocus
            label="Название"
            value={draft.name}
            onChange={(event) => setDraft((current) => ({ ...current, name: event.target.value }))}
            fullWidth
          />
          <TextField
            label="Категория"
            value={draft.category}
            onChange={(event) =>
              setDraft((current) => ({ ...current, category: event.target.value }))
            }
            fullWidth
          />
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <TextField
              label="Единица измерения"
              value={draft.unit}
              onChange={(event) =>
                setDraft((current) => ({ ...current, unit: event.target.value }))
              }
              fullWidth
            />
            <TextField
              label="Размер упаковки"
              type="number"
              value={draft.packageSize}
              onChange={(event) =>
                setDraft((current) => ({ ...current, packageSize: event.target.value }))
              }
              inputProps={{ min: 1 }}
              helperText="Необязательно"
              fullWidth
            />
          </Stack>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isSubmitting}>Отмена</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={isSubmitting}>
          {isSubmitting ? "Сохранение…" : product ? "Сохранить" : "Создать"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
