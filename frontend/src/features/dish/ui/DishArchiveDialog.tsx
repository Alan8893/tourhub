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

import type { ArchivedDish } from "../api/dishArchiveApi";
import type { Dish } from "../api/dishApi";
import {
  useArchiveDish,
  useArchivedDishes,
  useRestoreDish,
} from "../hooks/useDishArchive";
import { useDishes } from "../hooks/useDishes";
import { canRestoreArchivedDish, dishArchiveNotice } from "../model/dishArchive";

interface DishArchiveDialogProps {
  open: boolean;
  onClose: () => void;
  onArchived?: (dishId: string) => void;
}

type DishArchiveView = "active" | "archived";

function getErrorMessage(error: unknown): string {
  if (isAxiosError<{ error?: string; detail?: string }>(error)) {
    const message = error.response?.data?.error ?? error.response?.data?.detail;
    if (
      message === "Dish cannot be restored because it is blocked by the central alcohol policy"
    ) {
      return "Блюдо нельзя восстановить: центральная политика запрещает алкогольные позиции.";
    }
    return message ?? "Не удалось изменить состояние блюда.";
  }
  return error instanceof Error ? error.message : "Не удалось изменить состояние блюда.";
}

function isArchivedDish(dish: Dish | ArchivedDish): dish is ArchivedDish {
  return "archived_by_alcohol_policy" in dish;
}

function dishMeta(dish: Dish | ArchivedDish): string {
  if (isArchivedDish(dish)) return `Основной рецепт: ${dish.recipe_name}`;
  const variants = `${dish.recipes.length} ${dish.recipes.length === 1 ? "вариант" : "вариантов"}`;
  const roles = `${dish.meal_roles.length} ${dish.meal_roles.length === 1 ? "роль" : "ролей"}`;
  return `${dish.recipe.name} · ${variants} · ${roles}`;
}

export default function DishArchiveDialog({
  open,
  onClose,
  onArchived,
}: DishArchiveDialogProps) {
  const [view, setView] = useState<DishArchiveView>("active");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const activeQuery = useDishes();
  const archivedQuery = useArchivedDishes(open);
  const archiveMutation = useArchiveDish();
  const restoreMutation = useRestoreDish();
  const isMutating = archiveMutation.isPending || restoreMutation.isPending;

  useEffect(() => {
    if (open) {
      setView("active");
      setMessage(null);
      setError(null);
    }
  }, [open]);

  const archive = async (dish: Dish) => {
    if (!window.confirm(`Архивировать блюдо «${dish.name}»?`)) return;
    setMessage(null);
    setError(null);
    try {
      await archiveMutation.mutateAsync(dish.id);
      onArchived?.(dish.id);
      setMessage(`Блюдо «${dish.name}» перемещено в архив.`);
    } catch (mutationError) {
      setError(getErrorMessage(mutationError));
    }
  };

  const restore = async (dishId: string, dishName: string) => {
    setMessage(null);
    setError(null);
    try {
      await restoreMutation.mutateAsync(dishId);
      setMessage(`Блюдо «${dishName}» восстановлено.`);
    } catch (mutationError) {
      setError(getErrorMessage(mutationError));
    }
  };

  const query = view === "active" ? activeQuery : archivedQuery;
  const dishes = query.data?.items ?? [];

  return (
    <Dialog open={open} onClose={isMutating ? undefined : onClose} fullWidth maxWidth="md">
      <DialogTitle>Архив блюд</DialogTitle>
      <DialogContent>
        <Stack spacing={2.5} sx={{ mt: 1, minWidth: 0 }}>
          <Alert severity="info">
            Архивирование скрывает блюдо из нового выбора и автогенерации, но сохраняет рецепты,
            роли и все существующие назначения в меню и документах.
          </Alert>
          <ToggleButtonGroup
            exclusive
            size="small"
            value={view}
            onChange={(_, next: DishArchiveView | null) => {
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
              <CircularProgress aria-label="Загрузка каталога блюд" />
            </Box>
          )}
          {query.isError && (
            <Alert severity="error">
              {view === "active"
                ? "Не удалось загрузить активные блюда."
                : "Не удалось загрузить архив блюд."}
            </Alert>
          )}
          {!query.isLoading && !query.isError && dishes.length === 0 && (
            <Alert severity="info">
              {view === "active" ? "Активных блюд пока нет." : "Архив блюд пуст."}
            </Alert>
          )}

          {!query.isLoading && !query.isError && dishes.length > 0 && (
            <Stack spacing={1.5}>
              {dishes.map((dish) => {
                const archivedDish = isArchivedDish(dish) ? dish : null;
                const notice = archivedDish ? dishArchiveNotice(archivedDish) : null;
                const canRestore = archivedDish ? canRestoreArchivedDish(archivedDish) : false;
                return (
                  <Paper key={dish.id} variant="outlined" sx={{ p: 2, minWidth: 0 }}>
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
                          <Typography fontWeight={600}>{dish.name}</Typography>
                          {archivedDish?.archived_by_alcohol_policy && (
                            <Chip
                              size="small"
                              color="warning"
                              label="Заблокировано политикой"
                            />
                          )}
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                          {dishMeta(dish)}
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
                          onClick={() => void archive(dish as Dish)}
                          sx={{ flexShrink: 0 }}
                        >
                          {archiveMutation.isPending ? "Архивирование…" : "Архивировать"}
                        </Button>
                      ) : (
                        <Button
                          variant="contained"
                          disabled={!canRestore || isMutating}
                          onClick={() => void restore(dish.id, dish.name)}
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
        <Button onClick={onClose} disabled={isMutating}>
          Закрыть
        </Button>
      </DialogActions>
    </Dialog>
  );
}
