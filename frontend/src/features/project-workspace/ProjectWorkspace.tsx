import {
  Alert,
  Box,
  Button,
  Chip,
  Paper,
  Stack,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { useProject } from "@/features/project";
import { ProjectWorkflowProvider } from "@/features/project-workflow";
import { useModuleVisibility } from "@/features/system-settings/providers/ModuleVisibilityProvider";

import ProjectOverview from "./components/ProjectOverview";
import ProjectSettingsDialog from "./components/ProjectSettingsDialog";
import WorkflowModules from "./components/WorkflowModules";
import {
  buildProjectWorkspacePath,
  normalizeProjectWorkspaceSection,
  PROJECT_WORKSPACE_SECTIONS,
  type ProjectWorkspaceSection,
} from "./model/projectWorkspaceNavigation";

const mealLabels: Record<string, string> = {
  breakfast: "Завтрак",
  snack: "Перекус",
  lunch: "Обед",
  dinner: "Ужин",
};

const statusLabels: Record<string, string> = {
  draft: "Черновик",
  prepared: "Подготовлен",
  active: "Активный",
  completed: "Завершён",
};

function ProjectWorkspaceContent({
  projectId,
  section,
}: {
  projectId: number;
  section: ProjectWorkspaceSection;
}) {
  const navigate = useNavigate();
  const { data: project, isLoading, isError } = useProject(projectId);
  const { settings } = useModuleVisibility();
  const [settingsOpen, setSettingsOpen] = useState(false);

  const visibleSections = useMemo(
    () =>
      PROJECT_WORKSPACE_SECTIONS.filter((item) => {
        if (item.id === "shopping") return settings.shopping_visible;
        if (item.id === "equipment") return settings.equipment_visible;
        if (item.id === "documents") return settings.documents_visible;
        return true;
      }),
    [settings],
  );

  if (isLoading) {
    return <Typography>Загружаем проект…</Typography>;
  }

  if (isError || !project) {
    return <Alert severity="error">Проект не найден или у вас нет к нему доступа.</Alert>;
  }

  const settingsAvailable = Boolean(
    project.capabilities?.can_manage_project || project.capabilities?.can_delete,
  );

  return (
    <Stack spacing={2.5} sx={{ minWidth: 0, overflowX: "hidden" }}>
      <Box component="header">
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          <Link to="/projects" style={{ color: "inherit" }}>
            Проекты
          </Link>{" "}
          › {project.name}
        </Typography>

        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          alignItems={{ xs: "stretch", md: "flex-start" }}
          justifyContent="space-between"
        >
          <Stack spacing={0.75} sx={{ minWidth: 0 }}>
            <Typography variant="h4" component="h1" noWrap>
              {project.name}
            </Typography>
            <Stack
              direction="row"
              spacing={1}
              useFlexGap
              flexWrap="wrap"
              alignItems="center"
              color="text.secondary"
            >
              <Typography variant="body2">{project.participants} участников</Typography>
              <Typography variant="body2">•</Typography>
              <Typography variant="body2">{project.days} дня</Typography>
              {project.start_date && (
                <>
                  <Typography variant="body2">•</Typography>
                  <Typography variant="body2">с {project.start_date}</Typography>
                </>
              )}
              <Chip
                size="small"
                label={statusLabels[project.status] ?? project.status}
                variant={project.status === "completed" ? "outlined" : "filled"}
              />
            </Stack>
            <Typography variant="caption" color="text.secondary">
              Владелец: {project.owner_display_name ?? "не назначен"}
            </Typography>
            {project.first_meal && (
              <Typography variant="caption" color="text.secondary">
                Первый приём пищи: {mealLabels[project.first_meal] ?? project.first_meal}
              </Typography>
            )}
          </Stack>

          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
            {settingsAvailable && (
              <Button variant="outlined" onClick={() => setSettingsOpen(true)}>
                Настройки проекта
              </Button>
            )}
            {section !== "overview" && (
              <Button
                component={Link}
                to={buildProjectWorkspacePath(projectId, "overview")}
                variant="contained"
              >
                К обзору
              </Button>
            )}
          </Stack>
        </Stack>
      </Box>

      {project.status === "completed" && (
        <Alert severity="info">
          Проект завершён и доступен только для чтения. Функция «Копировать проект»
          запланирована отдельной задачей.
        </Alert>
      )}

      {!project.capabilities?.can_edit_menu && project.status !== "completed" && (
        <Alert severity="info">
          Вы приглашены в команду проекта. Меню и настройки доступны только для просмотра;
          закупки, снаряжение и документы остаются рабочими.
        </Alert>
      )}

      <Paper
        variant="outlined"
        sx={{
          position: "sticky",
          top: 0,
          zIndex: 2,
          bgcolor: "background.paper",
          minWidth: 0,
        }}
      >
        <Tabs
          value={section}
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
          aria-label="Разделы проекта"
        >
          {visibleSections.map((item) => (
            <Tab
              key={item.id}
              value={item.id}
              component={Link}
              to={buildProjectWorkspacePath(projectId, item.id)}
              label={`${item.icon} ${item.label}`}
            />
          ))}
        </Tabs>
      </Paper>

      {section === "overview" ? (
        <ProjectOverview project={project} />
      ) : (
        <WorkflowModules section={section} project={project} />
      )}

      {settingsAvailable && (
        <ProjectSettingsDialog
          open={settingsOpen}
          project={project}
          onClose={() => setSettingsOpen(false)}
          onDeleted={() => navigate("/projects", { replace: true })}
        />
      )}
    </Stack>
  );
}

export default function ProjectWorkspace() {
  const { id, section: rawSection } = useParams();
  const navigate = useNavigate();
  const projectId = Number(id ?? 0);
  const section = normalizeProjectWorkspaceSection(rawSection);

  useEffect(() => {
    if (rawSection && rawSection !== section && projectId > 0) {
      navigate(buildProjectWorkspacePath(projectId, "overview"), { replace: true });
    }
  }, [navigate, projectId, rawSection, section]);

  if (!Number.isInteger(projectId) || projectId <= 0) {
    return <Alert severity="error">Некорректный идентификатор проекта.</Alert>;
  }

  return (
    <ProjectWorkflowProvider projectId={projectId}>
      <ProjectWorkspaceContent projectId={projectId} section={section} />
    </ProjectWorkflowProvider>
  );
}
