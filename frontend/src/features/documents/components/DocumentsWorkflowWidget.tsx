import { useProjectWorkflow } from "@/features/project-workflow";

import DocumentsDownloadCard from "./DocumentsDownloadCard";

export default function DocumentsWorkflowWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const ready = Boolean(
    projectId &&
      preparationResult?.purchase_list_id &&
      preparationResult.purchase_checklist_id &&
      preparationResult.equipment_list_id,
  );

  return <DocumentsDownloadCard projectId={projectId} ready={ready} />;
}
