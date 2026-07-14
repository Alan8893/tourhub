import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";

import type { RecipeComponent, RecipeProduct } from "../api/recipeApi";
import {
  toRecipeComponentWriteInput,
  validateRecipeComponentDraft,
  type RecipeComponentDraft,
} from "../model/recipeEditor";

const initialDraft: RecipeComponentDraft = {
  productId: "",
  componentType: "base",
  amount: "",
  unit: "gram",
  calculationType: "per_person",
  peopleCount: "",
};

interface RecipeComponentDialogProps {
  open: boolean;
  products: RecipeProduct[];
  component: RecipeComponent | null;
  isSubmitting: boolean;
  errorMessage: string | null;
  onClose: () => void;
  onSubmit: (input: ReturnType<typeof toRecipeComponentWriteInput>) => void;
}

export default function RecipeComponentDialog({
  open,
  products,
  component,
  isSubmitting,
  errorMessage,
  onClose,
  onSubmit,
}: RecipeComponentDialogProps) {
  const [draft, setDraft] = useState<RecipeComponentDraft>(initialDraft);
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      return;
    }

    setValidationError(null);
    setDraft(
      component
        ? {
            productId: component.product.id,
            componentType: component.component_type as RecipeComponentDraft["componentType"],
            amount: String(component.amount),
            unit: component.unit,
            calculationType:
              component.calculation_type as RecipeComponentDraft["calculationType"],
            peopleCount: component.people_count ? String(component.people_count) : "",
          }
        : initialDraft,
    );
  }, [component, open]);

  const handleSubmit = () => {
    const error = validateRecipeComponentDraft(draft);
    setValidationError(error);
    if (error) {
      return;
    }

    onSubmit(toRecipeComponentWriteInput(draft));
  };

  return (
    <Dialog open={open} onClose={isSubmitting ? undefined : onClose} fullWidth maxWidth="sm">
      <DialogTitle>{component ? "Редактировать компонент" : "Добавить компонент"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          {(validationError || errorMessage) && (
            <Alert severity="error">{validationError ?? errorMessage}</Alert>
          )}

          <FormControl fullWidth>
            <InputLabel id="recipe-product-label">Продукт</InputLabel>
            <Select
              labelId="recipe-product-label"
              label="Продукт"
              value={draft.productId}
              onChange={(event) => {
                const productId = event.target.value;
                const product = products.find((item) => item.id === productId);
                setDraft((current) => ({
                  ...current,
                  productId,
                  unit: product?.unit ?? current.unit,
                }));
              }}
            >
              {products.map((product) => (
                <MenuItem key={product.id} value={product.id}>
                  {product.name}{product.category ? ` · ${product.category}` : ""}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="component-type-label">Роль компонента</InputLabel>
            <Select
              labelId="component-type-label"
              label="Роль компонента"
              value={draft.componentType}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  componentType: event.target.value as RecipeComponentDraft["componentType"],
                }))
              }
            >
              <MenuItem value="base">Основа</MenuItem>
              <MenuItem value="cooking">Для приготовления</MenuItem>
              <MenuItem value="optional">Дополнительно</MenuItem>
              <MenuItem value="serving_add_on">Для подачи</MenuItem>
            </Select>
          </FormControl>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <TextField
              label="Количество"
              type="number"
              value={draft.amount}
              onChange={(event) =>
                setDraft((current) => ({ ...current, amount: event.target.value }))
              }
              inputProps={{ min: 1 }}
              fullWidth
            />
            <TextField
              label="Единица"
              value={draft.unit}
              onChange={(event) =>
                setDraft((current) => ({ ...current, unit: event.target.value }))
              }
              fullWidth
            />
          </Stack>

          <FormControl fullWidth>
            <InputLabel id="calculation-type-label">Способ расчёта</InputLabel>
            <Select
              labelId="calculation-type-label"
              label="Способ расчёта"
              value={draft.calculationType}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  calculationType:
                    event.target.value as RecipeComponentDraft["calculationType"],
                  peopleCount:
                    event.target.value === "package_per_people" ? current.peopleCount : "",
                }))
              }
            >
              <MenuItem value="per_person">На человека</MenuItem>
              <MenuItem value="fixed_group">На всю группу</MenuItem>
              <MenuItem value="package_per_people">Упаковка на группу</MenuItem>
            </Select>
          </FormControl>

          {draft.calculationType === "package_per_people" && (
            <TextField
              label="Человек на упаковку"
              type="number"
              value={draft.peopleCount}
              onChange={(event) =>
                setDraft((current) => ({ ...current, peopleCount: event.target.value }))
              }
              inputProps={{ min: 1 }}
              fullWidth
            />
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isSubmitting}>
          Отмена
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={isSubmitting}>
          {isSubmitting ? "Сохранение…" : "Сохранить"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
