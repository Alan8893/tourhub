import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

import { useProjects } from "@/features/project/hooks/useProjects";

const statusLabels: Record<string, string> = {
  draft: "Черновик",
  prepared: "Подготовлен",
  active: "Активный",
  completed: "Завершён",
};

export default function ProjectsPage() {
  const navigate = useNavigate();
  const projectsQuery = useProjects();
  const projects = projectsQuery.data?.items ?? [];

  return (
    <Stack spacing={3} sx={{ mt: 4 }}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={2}
        justifyContent="space-between"
        alignItems={{ xs: "stretch", sm: "flex-start" }}
      >
        <Box>
          <Typography variant="h4" component="h1">Походы</Typography>
          <Typography color="text.secondary">
            Все проекты походов клуба. Откройте карточку, чтобы продолжить подготовку.
          </Typography>
        </Box>
        <Button variant="contained" onClick={() => navigate("/projects/new")}>Новый поход</Button>
      </Stack>

      {projectsQuery.isLoading && (
        <Stack alignItems="center" py={6}><CircularProgress aria-label="Загрузка походов" /></Stack>
      )}

      {projectsQuery.isError && (
        <Alert severity="error">Не удалось загрузить список походов.</Alert>
      )}

      {!projectsQuery.isLoading && !projectsQuery.isError && projects.length === 0 && (
        <Alert severity="info">Походов пока нет. Создайте первый проект.</Alert>
      )}

      {projects.length > 0 && (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", sm: "repeat(2, minmax(0, 1fr))", lg: "repeat(3, minmax(0, 1fr))" },
            gap: 2,
          }}
        >
          {projects.map((project) => (
            <Card key={project.id} variant="outlined">
              <CardActionArea onClick={() => navigate(`/projects/${project.id}`)} sx={{ height: "100%" }}>
                <CardContent>
                  <Stack spacing={1.5}>
                    <Stack direction="row" spacing={1} justifyContent="space-between" alignItems="flex-start">
                      <Typography variant="h6">{project.name}</Typography>
                      <Chip size="small" label={statusLabels[project.status] ?? project.status} />
                    </Stack>
                    <Typography variant="body2" color="text.secondary">
                      {project.start_date ? `Начало: ${project.start_date}` : "Дата начала не указана"}
                    </Typography>
                    <Typography variant="body2">
                      {project.days} дн. · {project.participants} участников
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Приёмы пищи: {project.first_meal ?? "не указан"} — {project.last_meal ?? "не указан"}
                    </Typography>
                  </Stack>
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Box>
      )}
    </Stack>
  );
}
