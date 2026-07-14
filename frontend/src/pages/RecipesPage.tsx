import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Divider,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";

import { useRecipe, useRecipes } from "@/features/recipe/hooks/useRecipes";
import { getRecipeLibraryViewState } from "@/features/recipe/model/recipeLibraryViewState";

const componentTypeLabels: Record<string, string> = {
  base: "Основа",
  cooking: "Для приготовления",
  optional: "Дополнительно",
  serving_add_on: "Для подачи",
};

const calculationTypeLabels: Record<string, string> = {
  per_person: "на человека",
  fixed_group: "на всю группу",
  package_per_people: "упаковка на группу",
};

export default function RecipesPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const recipesQuery = useRecipes();
  const recipeQuery = useRecipe(id);

  const recipes = recipesQuery.data?.items ?? [];
  const viewState = getRecipeLibraryViewState({
    isLoading: recipesQuery.isLoading,
    isError: recipesQuery.isError,
    recipeCount: recipes.length,
  });

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" component="h1">
          Рецепты
        </Typography>
        <Typography color="text.secondary">
          Библиотека походных рецептов и их продуктовых компонентов.
        </Typography>
      </Box>

      {viewState === "loading" && (
        <Stack alignItems="center" py={6}>
          <CircularProgress aria-label="Загрузка рецептов" />
        </Stack>
      )}

      {viewState === "error" && (
        <Alert severity="error">Не удалось загрузить библиотеку рецептов.</Alert>
      )}

      {viewState === "empty" && (
        <Alert severity="info">В библиотеке пока нет рецептов.</Alert>
      )}

      {viewState === "ready" && (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "minmax(260px, 360px) 1fr" },
            gap: 3,
            alignItems: "start",
          }}
        >
          <Paper variant="outlined">
            <List disablePadding>
              {recipes.map((recipe, index) => (
                <Box key={recipe.id}>
                  {index > 0 && <Divider />}
                  <ListItemButton
                    selected={recipe.id === id}
                    onClick={() => navigate(`/recipes/${recipe.id}`)}
                  >
                    <ListItemText
                      primary={recipe.name}
                      secondary={`${recipe.component_count} компонентов · ${recipe.note_count} заметок`}
                    />
                  </ListItemButton>
                </Box>
              ))}
            </List>
          </Paper>

          <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 }, minHeight: 240 }}>
            {!id && (
              <Stack spacing={1} alignItems="center" justifyContent="center" minHeight={190}>
                <Typography variant="h6">Выберите рецепт</Typography>
                <Typography color="text.secondary" textAlign="center">
                  Компоненты и заметки выбранного рецепта появятся здесь.
                </Typography>
              </Stack>
            )}

            {id && recipeQuery.isLoading && (
              <Stack alignItems="center" py={6}>
                <CircularProgress aria-label="Загрузка рецепта" />
              </Stack>
            )}

            {id && recipeQuery.isError && (
              <Alert severity="error">Не удалось загрузить выбранный рецепт.</Alert>
            )}

            {recipeQuery.data && (
              <Stack spacing={3}>
                <Box>
                  <Typography variant="h5" component="h2">
                    {recipeQuery.data.name}
                  </Typography>
                  <Typography color="text.secondary">
                    {recipeQuery.data.components.length} компонентов · {recipeQuery.data.notes.length}{" "}
                    заметок
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="h6" gutterBottom>
                    Состав
                  </Typography>
                  {recipeQuery.data.components.length === 0 ? (
                    <Typography color="text.secondary">Компоненты пока не добавлены.</Typography>
                  ) : (
                    <Stack spacing={1.5}>
                      {recipeQuery.data.components.map((component) => (
                        <Paper key={component.id} variant="outlined" sx={{ p: 2 }}>
                          <Stack
                            direction={{ xs: "column", sm: "row" }}
                            spacing={1}
                            justifyContent="space-between"
                          >
                            <Box>
                              <Typography fontWeight={600}>{component.product.name}</Typography>
                              <Typography variant="body2" color="text.secondary">
                                {component.product.category ?? "Без категории"}
                              </Typography>
                            </Box>
                            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                              <Chip
                                size="small"
                                label={componentTypeLabels[component.component_type] ?? component.component_type}
                              />
                              <Chip
                                size="small"
                                variant="outlined"
                                label={`${component.amount} ${component.unit}`}
                              />
                            </Stack>
                          </Stack>
                          <Typography variant="body2" sx={{ mt: 1 }}>
                            Расчёт: {calculationTypeLabels[component.calculation_type] ?? component.calculation_type}
                            {component.people_count ? `, на ${component.people_count} чел.` : ""}
                          </Typography>
                          {component.product.package_size && (
                            <Typography variant="body2" color="text.secondary">
                              Упаковка: {component.product.package_size} {component.product.unit}
                            </Typography>
                          )}
                        </Paper>
                      ))}
                    </Stack>
                  )}
                </Box>

                <Box>
                  <Typography variant="h6" gutterBottom>
                    Заметки
                  </Typography>
                  {recipeQuery.data.notes.length === 0 ? (
                    <Typography color="text.secondary">Заметок пока нет.</Typography>
                  ) : (
                    <Stack spacing={1.5}>
                      {recipeQuery.data.notes.map((note) => (
                        <Alert key={note.id} severity="info" icon={false}>
                          {note.text}
                        </Alert>
                      ))}
                    </Stack>
                  )}
                </Box>
              </Stack>
            )}
          </Paper>
        </Box>
      )}
    </Stack>
  );
}
