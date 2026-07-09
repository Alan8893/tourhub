import { Box, Typography } from "@mui/material";

import type { Project } from "../api/projectApi";

interface Props {
  project: Project;
}

const mealLabels: Record<string, string> = {
  breakfast: "Завтрак",
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
