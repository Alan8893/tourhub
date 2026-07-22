import { Alert, Box, Paper, Tab, Tabs } from "@mui/material";
import { useState } from "react";

import { DocumentsWidget } from "@/features/documents";
import CampInventoryWidget from "@/features/equipment/components/CampInventoryWidget";
import { MealPlanWidget } from "@/features/meal-plan";
import type { Project } from "@/features/project/api/projectApi";
import { PurchaseWidget } from "@/features/purchase";
import { ShoppingWidget } from "@/features/shopping";
import { useModuleVisibility } from "@/features/system-settings/providers/ModuleVisibilityProvider";

import type { ProjectWorkspaceSection } from "../model/projectWorkspaceNavigation";

function ShoppingWorkspace({ readOnly }: { readOnly: boolean }) {
  const [activeView, setActiveView] = useState<"calculation" | "checklist">(
    "calculation",
  );

  return (
    <Box>
      <Paper variant="outlined" sx={{ mb: 2 }}>
        <Tabs
          value={activeView}
          onChange={(_, value: "calculation" | "checklist") =>
            setActiveView(value)
          }
          variant="fullWidth"
          aria-label="Раздел закупки"
        >
          <Tab value="calculation" label="Расчёт и фасовка" />
          <Tab value="checklist" label="Чек-лист" />
        </Tabs>
      </Paper>

      {activeView === "calculation" ? (
        <ShoppingWidget readOnly={readOnly} />
      ) : (
        <PurchaseWidget readOnly={readOnly} />
      )}
    </Box>
  );
}

interface WorkflowModulesProps {
  section: Exclude<ProjectWorkspaceSection, "overview">;
  project: Project;
}

export default function WorkflowModules({ section, project }: WorkflowModulesProps) {
  const { settings } = useModuleVisibility();

  if (section === "menu") {
    return <MealPlanWidget readOnly={!project.capabilities?.can_edit_menu} />;
  }

  if (section === "shopping") {
    return settings.shopping_visible ? (
      <ShoppingWorkspace readOnly={!project.capabilities?.can_operate_shopping} />
    ) : (
      <Alert severity="info">Раздел закупки отключён в настройках модулей.</Alert>
    );
  }

  if (section === "equipment") {
    return settings.equipment_visible ? (
      <CampInventoryWidget readOnly={!project.capabilities?.can_operate_equipment} />
    ) : (
      <Alert severity="info">Раздел оборудования отключён в настройках модулей.</Alert>
    );
  }

  return settings.documents_visible ? (
    <DocumentsWidget />
  ) : (
    <Alert severity="info">Раздел документов отключён в настройках модулей.</Alert>
  );
}
