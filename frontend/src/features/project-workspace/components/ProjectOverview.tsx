import {
  Button,
  Card,
  CardContent,
  Grid,
  Stack,
  Typography,
} from "@mui/material";
import { Link } from "react-router-dom";

import { useProjectWorkflow } from "@/features/project-workflow";
import { useModuleVisibility } from "@/features/system-settings/providers/ModuleVisibilityProvider";

import { buildProjectWorkspacePath } from "../model/projectWorkspaceNavigation";
import NextWorkflowAction from "./NextWorkflowAction";
import ProjectWorkflowPanel from "./ProjectWorkflowPanel";

interface SummaryCardProps {
  title: string;
  detail: string;
  actionLabel: string;
  to: string;
}

function SummaryCard({ title, detail, actionLabel, to }: SummaryCardProps) {
  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      <CardContent>
        <Stack spacing={1.5} alignItems="flex-start" sx={{ height: "100%" }}>
          <Stack spacing={0.5} sx={{ flex: 1 }}>
            <Typography variant="h6">{title}</Typography>
            <Typography variant="body2" color="text.secondary">
              {detail}
            </Typography>
          </Stack>
          <Button component={Link} to={to} variant="outlined" size="small">
            {actionLabel}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}

export default function ProjectOverview() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const { settings } = useModuleVisibility();
  const hasMenu = Boolean(preparationResult?.meal_plan_id);
  const hasShopping = Boolean(preparationResult?.purchase_list_id);
  const hasChecklist = Boolean(preparationResult?.purchase_checklist_id);
  const hasEquipment = Boolean(preparationResult?.equipment_list_id);
  const hasDocuments = hasShopping && hasChecklist && hasEquipment;

  return (
    <Stack spacing={2}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={5}>
          <ProjectWorkflowPanel />
        </Grid>
        <Grid item xs={12} md={7}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <SummaryCard
                title="Меню"
                detail={hasMenu ? "Меню сформировано и доступно для редактирования." : "Сформируйте меню похода."}
                actionLabel="Открыть меню"
                to={buildProjectWorkspacePath(projectId, "menu")}
              />
            </Grid>
            {settings.shopping_visible && (
              <Grid item xs={12} sm={6}>
                <SummaryCard
                  title="Закупка"
                  detail={
                    hasShopping && hasChecklist
                      ? "Расчёт фасовки и чек-лист готовы."
                      : "Подготовьте расчёт и чек-лист покупок."
                  }
                  actionLabel="Открыть закупку"
                  to={buildProjectWorkspacePath(projectId, "shopping")}
                />
              </Grid>
            )}
            {settings.equipment_visible && (
              <Grid item xs={12} sm={6}>
                <SummaryCard
                  title="Оборудование"
                  detail={hasEquipment ? "Список оборудования сформирован." : "Список появится после подготовки проекта."}
                  actionLabel="Открыть"
                  to={buildProjectWorkspacePath(projectId, "equipment")}
                />
              </Grid>
            )}
            {settings.documents_visible && (
              <Grid item xs={12} sm={6}>
                <SummaryCard
                  title="Документы"
                  detail={hasDocuments ? "PDF, Excel и полный пакет готовы к скачиванию." : "Документы появятся после подготовки проекта."}
                  actionLabel="Открыть документы"
                  to={buildProjectWorkspacePath(projectId, "documents")}
                />
              </Grid>
            )}
          </Grid>
        </Grid>
      </Grid>

      <NextWorkflowAction />
    </Stack>
  );
}
