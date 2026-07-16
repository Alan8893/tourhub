import { Container, CssBaseline } from "@mui/material";
import { StrictMode, useEffect } from "react";
import { createRoot } from "react-dom/client";

import DocumentsWidget from "@/features/documents/components/DocumentsWidget";
import {
  ProjectWorkflowProvider,
  useProjectWorkflow,
} from "@/features/project-workflow";

function PreparedDocuments() {
  const { setPreparationResult } = useProjectWorkflow();

  useEffect(() => {
    setPreparationResult({
      project_id: 76,
      meal_plan_id: "meal-plan-76",
      purchase_list_id: "purchase-list-76",
      purchase_checklist_id: "purchase-checklist-76",
      equipment_list_id: "equipment-list-76",
    });
  }, [setPreparationResult]);

  return <DocumentsWidget />;
}

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ProjectWorkflowProvider projectId={76}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ p: 1 }}>
        <PreparedDocuments />
      </Container>
    </ProjectWorkflowProvider>
  </StrictMode>,
);
