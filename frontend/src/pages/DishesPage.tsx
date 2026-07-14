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
  Divider,
  List,
  ListItemButton,
  ListItemText,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { isAxiosError } from "axios";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { useCreateDish, useDish, useDishes, useUpdateDish } from "@/features/dish/hooks/useDishes";
import { toDishWriteInput } from "@/features/dish/model/dishEditor";
import { useRecipes } from "@/features/recipe/hooks/useRecipes";

function getErrorMessage(error: unknown): string {
  if (isAxiosError<{ error?: string }>(error)) {
    return error.response?.data?.error ?? "Не удалось сохранить блюдо.";
  }
  return error instanceof Error ? error.message : "Не удалось сохранить блюдо.";
}

export default function DishesPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const dishesQuery = useDishes();
  const dishQuery = useDish(id);
  const recipesQuery = useRecipes(false);
  const createMutation = useCreateDish();
  const updateMutation = useUpdateDish();
  const [dialogMode, setDialogMode] = useState<"create" | "edit" | null>(null);
  const [name, setName] = useState("");
  const [recipeId, setRecipeId] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const dishes = dishesQuery.data?.items ?? [];
  const activeRecipes = recipesQuery.data?.items.filter((recipe) => !recipe.is_archived) ?? [];
  const mutation = dialogMode === "create" ? createMutation : updateMutation;

  const openCreate = () => {
    setName("");
    setRecipeId(activeRecipes[0]?.id ?? "");
    setFormError(null);
    createMutation.reset();
    setDialogMode("create");
  };

  const openEdit = () => {
    if (!dishQuery.data) return;
    setName(dishQuery.data.name);
    setRecipeId(dishQuery.data.recipe.is_archived ? "" : dishQuery.data.recipe.id);
    setFormError(null);
    updateMutation.reset();
    setDialogMode("edit");
  };

  const submit = async () => {
    try {
      const input = toDishWriteInput({ name, recipeId });
      if (dialogMode === "create") {
        const dish = await createMutation.mutateAsync(input);
        setDialogMode(null);
        navigate(`/dishes/${dish.id}`);
      } else if (dialogMode === "edit" && id) {
        await updateMutation.mutateAsync({ dishId: id, input });
        setDialogMode(null);
      }
    } catch (error) {
      setFormError(getErrorMessage(error));
    }
  };

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} justifyContent="space-between">
        <Box>
          <Typography variant="h4" component="h1">Блюда</Typography>
          <Typography color="text.secondary">Каталог блюд и назначенных им рецептов.</Typography>
        </Box>
        <Button variant="contained" onClick={openCreate} disabled={recipesQuery.isLoading || activeRecipes.length === 0}>
          Создать блюдо
        </Button>
      </Stack>

      {recipesQuery.isSuccess && activeRecipes.length === 0 && (
        <Alert severity="info">Сначала создайте активный рецепт в разделе «Рецепты».</Alert>
      )}
      {dishesQuery.isLoading && <Stack alignItems="center" py={6}><CircularProgress /></Stack>}
      {dishesQuery.isError && <Alert severity="error">Не удалось загрузить каталог блюд.</Alert>}
      {dishesQuery.isSuccess && dishes.length === 0 && (
        <Alert severity="info">Блюд пока нет. Создайте первое блюдо.</Alert>
      )}

      {dishes.length > 0 && (
        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "minmax(260px, 360px) 1fr" }, gap: 3 }}>
          <Paper variant="outlined">
            <List disablePadding>
              {dishes.map((dish, index) => (
                <Box key={dish.id}>
                  {index > 0 && <Divider />}
                  <ListItemButton selected={dish.id === id} onClick={() => navigate(`/dishes/${dish.id}`)}>
                    <ListItemText primary={dish.name} secondary={dish.recipe.name} />
                  </ListItemButton>
                </Box>
              ))}
            </List>
          </Paper>

          <Paper variant="outlined" sx={{ p: 3, minHeight: 220 }}>
            {!id && <Typography color="text.secondary">Выберите блюдо для просмотра.</Typography>}
            {id && dishQuery.isLoading && <Stack alignItems="center" py={5}><CircularProgress /></Stack>}
            {id && dishQuery.isError && <Alert severity="error">Не удалось загрузить блюдо.</Alert>}
            {dishQuery.data && (
              <Stack spacing={2}>
                <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" spacing={2}>
                  <Box>
                    <Typography variant="h5">{dishQuery.data.name}</Typography>
                    <Stack direction="row" spacing={1} mt={1} alignItems="center">
                      <Typography color="text.secondary">Рецепт: {dishQuery.data.recipe.name}</Typography>
                      {dishQuery.data.recipe.is_archived && <Chip size="small" label="Рецепт в архиве" />}
                    </Stack>
                  </Box>
                  <Button variant="outlined" onClick={openEdit}>Изменить</Button>
                </Stack>
                {dishQuery.data.recipe.is_archived && (
                  <Alert severity="warning">Чтобы сохранить изменения, выберите активный рецепт.</Alert>
                )}
                <Button onClick={() => navigate(`/recipes/${dishQuery.data.recipe.id}`)} sx={{ alignSelf: "flex-start" }}>
                  Открыть рецепт
                </Button>
              </Stack>
            )}
          </Paper>
        </Box>
      )}

      <Dialog open={dialogMode !== null} onClose={mutation.isPending ? undefined : () => setDialogMode(null)} fullWidth maxWidth="sm">
        <DialogTitle>{dialogMode === "create" ? "Новое блюдо" : "Изменить блюдо"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            {(formError || mutation.isError) && <Alert severity="error">{formError ?? getErrorMessage(mutation.error)}</Alert>}
            <TextField label="Название" value={name} onChange={(event) => setName(event.target.value)} autoFocus fullWidth />
            <TextField select label="Рецепт" value={recipeId} onChange={(event) => setRecipeId(event.target.value)} fullWidth>
              {activeRecipes.map((recipe) => <MenuItem key={recipe.id} value={recipe.id}>{recipe.name}</MenuItem>)}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogMode(null)} disabled={mutation.isPending}>Отмена</Button>
          <Button variant="contained" onClick={() => void submit()} disabled={mutation.isPending}>Сохранить</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
