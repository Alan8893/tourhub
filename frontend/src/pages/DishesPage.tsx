import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControlLabel,
  FormGroup,
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
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  useCreateDish,
  useDish,
  useDishes,
  useUpdateDish,
  useUpdateDishMealRoles,
} from "@/features/dish/hooks/useDishes";
import {
  MEAL_ROLE_OPTIONS,
  MEAL_TYPE_OPTIONS,
  createMealRoleDraft,
  formatMealRoleSummary,
  formatMealTypeSummary,
  getMealRoleOption,
  setMealRoleMealTypeSelected,
  setMealRoleRepeatable,
  setMealRoleSelected,
  toDishMealRolesWriteInput,
  toDishWriteInput,
  type MealRoleDraft,
} from "@/features/dish/model/dishEditor";
import { useRecipes } from "@/features/recipe/hooks/useRecipes";

function getErrorMessage(error: unknown, fallback: string): string {
  if (isAxiosError<{ error?: string }>(error)) {
    return error.response?.data?.error ?? fallback;
  }
  return error instanceof Error ? error.message : fallback;
}

function uniqueRecipeIds(defaultRecipeId: string, recipeIds: string[]): string[] {
  return Array.from(new Set([defaultRecipeId, ...recipeIds].filter(Boolean)));
}

export default function DishesPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const dishesQuery = useDishes();
  const dishQuery = useDish(id);
  const recipesQuery = useRecipes(false);
  const createMutation = useCreateDish();
  const updateMutation = useUpdateDish();
  const roleMutation = useUpdateDishMealRoles();
  const [dialogMode, setDialogMode] = useState<"create" | "edit" | null>(null);
  const [name, setName] = useState("");
  const [recipeId, setRecipeId] = useState("");
  const [recipeIds, setRecipeIds] = useState<string[]>([]);
  const [formError, setFormError] = useState<string | null>(null);
  const [roleDialogOpen, setRoleDialogOpen] = useState(false);
  const [roleDraft, setRoleDraft] = useState<MealRoleDraft>(() => createMealRoleDraft([]));
  const [roleError, setRoleError] = useState<string | null>(null);
  const [roleFeedback, setRoleFeedback] = useState<string | null>(null);

  const dishes = dishesQuery.data?.items ?? [];
  const activeRecipes = recipesQuery.data?.items.filter((recipe) => !recipe.is_archived) ?? [];
  const defaultRecipes = activeRecipes.filter(
    (recipe) => recipe.scope === "club" && recipe.lifecycle_status === "published",
  );
  const mutation = dialogMode === "create" ? createMutation : updateMutation;

  useEffect(() => {
    setRoleDialogOpen(false);
    setRoleFeedback(null);
  }, [id]);

  const openCreate = () => {
    const defaultRecipeId = defaultRecipes[0]?.id ?? "";
    setName("");
    setRecipeId(defaultRecipeId);
    setRecipeIds(defaultRecipeId ? [defaultRecipeId] : []);
    setFormError(null);
    createMutation.reset();
    setDialogMode("create");
  };

  const openEdit = () => {
    if (!dishQuery.data) return;
    const defaultRecipeId = dishQuery.data.recipe.is_archived ? "" : dishQuery.data.recipe.id;
    setName(dishQuery.data.name);
    setRecipeId(defaultRecipeId);
    setRecipeIds(uniqueRecipeIds(
      defaultRecipeId,
      dishQuery.data.recipes.filter((recipe) => !recipe.is_archived).map((recipe) => recipe.id),
    ));
    setFormError(null);
    updateMutation.reset();
    setDialogMode("edit");
  };

  const openRoleEditor = () => {
    if (!dishQuery.data) return;
    setRoleDraft(createMealRoleDraft(dishQuery.data.meal_roles));
    setRoleError(null);
    roleMutation.reset();
    setRoleDialogOpen(true);
  };

  const submit = async () => {
    try {
      const input = {
        ...toDishWriteInput({ name, recipeId }),
        recipe_ids: uniqueRecipeIds(recipeId, recipeIds),
      };
      if (dialogMode === "create") {
        const dish = await createMutation.mutateAsync(input);
        setDialogMode(null);
        navigate(`/dishes/${dish.id}`);
      } else if (dialogMode === "edit" && id) {
        await updateMutation.mutateAsync({ dishId: id, input });
        setDialogMode(null);
      }
    } catch (error) {
      setFormError(getErrorMessage(error, "Не удалось сохранить блюдо."));
    }
  };

  const submitMealRoles = async () => {
    if (!id) return;
    try {
      await roleMutation.mutateAsync({
        dishId: id,
        input: toDishMealRolesWriteInput(roleDraft),
      });
      setRoleDialogOpen(false);
      setRoleFeedback("Роли блюда сохранены.");
    } catch (error) {
      setRoleError(getErrorMessage(error, "Не удалось сохранить роли блюда."));
    }
  };

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} justifyContent="space-between">
        <Box>
          <Typography variant="h4" component="h1">Блюда</Typography>
          <Typography color="text.secondary">Каталог блюд, вариантов рецептов и ролей в составе меню.</Typography>
        </Box>
        <Button
          variant="contained"
          onClick={openCreate}
          disabled={recipesQuery.isLoading || defaultRecipes.length === 0}
        >
          Создать блюдо
        </Button>
      </Stack>

      {recipesQuery.isSuccess && defaultRecipes.length === 0 && (
        <Alert severity="info">
          Для создания блюда нужен хотя бы один опубликованный клубный рецепт.
        </Alert>
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
                    <ListItemText
                      primary={dish.name}
                      secondary={`${dish.recipe.name} · ${dish.recipes.length} вариантов · ${formatMealRoleSummary(dish.meal_roles)}`}
                    />
                  </ListItemButton>
                </Box>
              ))}
            </List>
          </Paper>

          <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 }, minHeight: 220 }}>
            {!id && <Typography color="text.secondary">Выберите блюдо для просмотра.</Typography>}
            {id && dishQuery.isLoading && <Stack alignItems="center" py={5}><CircularProgress /></Stack>}
            {id && dishQuery.isError && <Alert severity="error">Не удалось загрузить блюдо.</Alert>}
            {dishQuery.data && (
              <Stack spacing={2}>
                {roleFeedback && <Alert severity="success">{roleFeedback}</Alert>}
                <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" spacing={2}>
                  <Box>
                    <Typography variant="h5">{dishQuery.data.name}</Typography>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1} mt={1} alignItems={{ sm: "center" }}>
                      <Typography color="text.secondary">Рецепт: {dishQuery.data.recipe.name}</Typography>
                      <Chip size="small" label="Основной клубный" />
                      {dishQuery.data.recipe.is_archived && <Chip size="small" color="warning" label="Рецепт в архиве" />}
                    </Stack>
                  </Box>
                  <Button variant="outlined" onClick={openEdit}>Изменить</Button>
                </Stack>
                {dishQuery.data.recipe.is_archived && (
                  <Alert severity="warning">Чтобы сохранить изменения, выберите активный опубликованный клубный рецепт.</Alert>
                )}
                <Button onClick={() => navigate(`/recipes/${dishQuery.data.recipe.id}`)} sx={{ alignSelf: "flex-start" }}>
                  Открыть рецепт
                </Button>

                <Divider />

                <Stack spacing={1.5}>
                  <Box>
                    <Typography variant="h6">Варианты рецепта</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Генератор выбирает один из этих вариантов по режиму конкретного похода и сохраняет точный выбор в меню.
                    </Typography>
                  </Box>
                  <Stack spacing={1}>
                    {dishQuery.data.recipes.map((recipe) => (
                      <Paper key={recipe.id} variant="outlined" sx={{ p: 1.5 }}>
                        <Stack
                          direction={{ xs: "column", sm: "row" }}
                          spacing={1}
                          justifyContent="space-between"
                          alignItems={{ sm: "center" }}
                        >
                          <Box sx={{ minWidth: 0 }}>
                            <Typography fontWeight={600}>{recipe.name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {recipe.scope === "club"
                                ? "Клубный рецепт"
                                : `Личный рецепт${recipe.owner_display_name ? ` · ${recipe.owner_display_name}` : ""}`}
                            </Typography>
                          </Box>
                          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                            {recipe.is_default && <Chip size="small" label="Основной" />}
                            <Chip size="small" variant="outlined" label={recipe.scope === "club" ? "CLUB" : "PERSONAL"} />
                            {recipe.is_archived && <Chip size="small" color="warning" label="Архив" />}
                            <Button size="small" onClick={() => navigate(`/recipes/${recipe.id}`)}>Открыть</Button>
                          </Stack>
                        </Stack>
                      </Paper>
                    ))}
                  </Stack>
                </Stack>

                <Divider />

                <Stack spacing={1.5}>
                  <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} justifyContent="space-between" alignItems={{ sm: "center" }}>
                    <Box>
                      <Typography variant="h6">Роли в меню</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Роль задаёт назначение блюда, а приёмы пищи — где генератор вправе его использовать.
                      </Typography>
                    </Box>
                    <Button variant="outlined" onClick={openRoleEditor}>Настроить роли</Button>
                  </Stack>

                  {dishQuery.data.meal_roles.length === 0 ? (
                    <Alert severity="info">
                      Роли не назначены. Блюдо доступно для ручного выбора, но не будет участвовать в ролевой автогенерации.
                    </Alert>
                  ) : (
                    <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ minWidth: 0 }}>
                      {dishQuery.data.meal_roles.map((assignment) => (
                        <Chip
                          key={assignment.role}
                          label={`${getMealRoleOption(assignment.role).shortLabel}: ${formatMealTypeSummary(assignment.allowed_meal_types)}${assignment.is_repeatable ? " · можно повторять" : ""}`}
                          sx={{
                            maxWidth: "100%",
                            height: "auto",
                            "& .MuiChip-label": {
                              display: "block",
                              py: 0.75,
                              whiteSpace: "normal",
                            },
                          }}
                        />
                      ))}
                    </Stack>
                  )}
                </Stack>
              </Stack>
            )}
          </Paper>
        </Box>
      )}

      <Dialog open={dialogMode !== null} onClose={mutation.isPending ? undefined : () => setDialogMode(null)} fullWidth maxWidth="sm">
        <DialogTitle>{dialogMode === "create" ? "Новое блюдо" : "Изменить блюдо"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            {(formError || mutation.isError) && (
              <Alert severity="error">{formError ?? getErrorMessage(mutation.error, "Не удалось сохранить блюдо.")}</Alert>
            )}
            <TextField label="Название" value={name} onChange={(event) => setName(event.target.value)} autoFocus fullWidth />
            <TextField
              select
              label="Основной клубный рецепт"
              value={recipeId}
              onChange={(event) => {
                const nextRecipeId = event.target.value;
                setRecipeId(nextRecipeId);
                setRecipeIds((current) => uniqueRecipeIds(nextRecipeId, current));
              }}
              helperText="Основной вариант всегда должен быть опубликованным клубным рецептом."
              fullWidth
            >
              {defaultRecipes.map((recipe) => <MenuItem key={recipe.id} value={recipe.id}>{recipe.name}</MenuItem>)}
            </TextField>
            <TextField
              select
              label="Варианты рецепта"
              value={recipeIds}
              onChange={(event) => {
                const value = event.target.value;
                const selected = typeof value === "string" ? value.split(",") : value;
                setRecipeIds(uniqueRecipeIds(recipeId, selected));
              }}
              SelectProps={{
                multiple: true,
                renderValue: (selected) => {
                  const selectedIds = selected as string[];
                  return activeRecipes
                    .filter((recipe) => selectedIds.includes(recipe.id))
                    .map((recipe) => recipe.name)
                    .join(", ");
                },
              }}
              helperText="Можно добавить опубликованные клубные и доступные вам личные рецепты."
              fullWidth
            >
              {activeRecipes.map((recipe) => (
                <MenuItem key={recipe.id} value={recipe.id}>
                  <Checkbox checked={recipeIds.includes(recipe.id)} />
                  <ListItemText
                    primary={recipe.name}
                    secondary={recipe.scope === "club"
                      ? "Клубный рецепт"
                      : `Личный рецепт${recipe.owner_display_name ? ` · ${recipe.owner_display_name}` : ""}`}
                  />
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogMode(null)} disabled={mutation.isPending}>Отмена</Button>
          <Button variant="contained" onClick={() => void submit()} disabled={mutation.isPending || !recipeId}>Сохранить</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={roleDialogOpen}
        onClose={roleMutation.isPending ? undefined : () => setRoleDialogOpen(false)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Роли блюда{dishQuery.data ? ` «${dishQuery.data.name}»` : ""}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            {(roleError || roleMutation.isError) && (
              <Alert severity="error">
                {roleError ?? getErrorMessage(roleMutation.error, "Не удалось сохранить роли блюда.")}
              </Alert>
            )}
            <Alert severity="info">
              Для каждой роли обязательно укажите допустимые приёмы пищи. Борщ можно ограничить обедом и ужином, а кашу — завтраком.
            </Alert>
            <FormGroup sx={{ gap: 1.5 }}>
              {MEAL_ROLE_OPTIONS.map((option) => {
                const item = roleDraft[option.role];
                const mealTypeOptions = MEAL_TYPE_OPTIONS.filter(({ mealType }) => (
                  option.allowedMealTypes.includes(mealType)
                ));
                return (
                  <Paper key={option.role} variant="outlined" sx={{ p: 1.5 }}>
                    <FormControlLabel
                      sx={{ m: 0, alignItems: "flex-start" }}
                      control={(
                        <Checkbox
                          checked={item.selected}
                          onChange={(event) => setRoleDraft((current) => (
                            setMealRoleSelected(current, option.role, event.target.checked)
                          ))}
                          inputProps={{ "aria-label": `Назначить роль «${option.label}»` }}
                        />
                      )}
                      label={(
                        <Box pt={0.75}>
                          <Typography fontWeight={600}>{option.label}</Typography>
                          <Typography variant="body2" color="text.secondary">{option.description}</Typography>
                        </Box>
                      )}
                    />
                    {item.selected && (
                      <Box sx={{ ml: { xs: 0, sm: 4 }, mt: 1 }}>
                        <Typography variant="body2" fontWeight={600} mb={0.5}>
                          Допустимые приёмы пищи
                        </Typography>
                        <FormGroup row sx={{ gap: { xs: 0, sm: 0.5 } }}>
                          {mealTypeOptions.map((mealTypeOption) => (
                            <FormControlLabel
                              key={mealTypeOption.mealType}
                              sx={{ mr: 1 }}
                              control={(
                                <Checkbox
                                  size="small"
                                  checked={item.allowedMealTypes[mealTypeOption.mealType]}
                                  onChange={(event) => setRoleDraft((current) => (
                                    setMealRoleMealTypeSelected(
                                      current,
                                      option.role,
                                      mealTypeOption.mealType,
                                      event.target.checked,
                                    )
                                  ))}
                                  inputProps={{
                                    "aria-label": `Разрешить роль «${option.label}» для приёма пищи «${mealTypeOption.label}»`,
                                  }}
                                />
                              )}
                              label={mealTypeOption.label}
                            />
                          ))}
                        </FormGroup>
                      </Box>
                    )}
                    <FormControlLabel
                      sx={{ ml: { xs: 0, sm: 4 }, mt: 0.5 }}
                      control={(
                        <Checkbox
                          size="small"
                          checked={item.isRepeatable}
                          disabled={!item.selected}
                          onChange={(event) => setRoleDraft((current) => (
                            setMealRoleRepeatable(current, option.role, event.target.checked)
                          ))}
                          inputProps={{ "aria-label": `Разрешить повторение роли «${option.label}»` }}
                        />
                      )}
                      label="Разрешить повторение при автогенерации"
                    />
                  </Paper>
                );
              })}
            </FormGroup>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRoleDialogOpen(false)} disabled={roleMutation.isPending}>Отмена</Button>
          <Button variant="contained" onClick={() => void submitMealRoles()} disabled={roleMutation.isPending}>
            Сохранить роли
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
