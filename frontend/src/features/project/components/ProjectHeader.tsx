import { Box, Chip, Stack, Typography } from "@mui/material";

import type { Project } from "../api/projectApi";
import { getRecipeGenerationModeLabel } from "../model/recipeGenerationMode";

interface Props {
  project: Project;
}

const mealLabels: Record<string, string> = {
  breakfast: "Завтрак",
  snack: "Перекус",
  lunch: "Обед",
  dinner: "Ужин",
};

export default function ProjectHeader({ project }: Props) {
  return (
    <Box>
      <Typography variant="h4">{project.name}</Typography>

      <Typography variant="body1" sx={{ mt: 1 }}>
        👥 Участники: {project.participants} · 📅 Длительность: {project.days} дней · Статус: {project.status}
      </Typography>

      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1 }}>
        <Chip
          size="small"
          variant="outlined"
          label={`Рецепты: ${getRecipeGenerationModeLabel(project.recipe_generation_mode)}`}
        />
      </Stack>

      {project.start_date && (
        <Typography variant="body2" sx={{ mt: 0.5 }}>
          🗓 Дата начала: {project.start_date}
        </Typography>
      )}

      {project.first_meal && (
        <Typography variant="body2" sx={{ mt: 0.5 }}>
          🍽 Первый приём пищи: {mealLabels[project.first_meal] ?? project.first_meal}
        </Typography>
      )}
    </Box>
  );
}
