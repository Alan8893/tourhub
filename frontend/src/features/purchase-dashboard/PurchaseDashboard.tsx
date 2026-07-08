import { Typography } from "@mui/material";

import { useMeta } from "../meta/hooks/useMeta";
import Loading from "../../shared/ui/Loading";
import ErrorMessage from "../../shared/ui/ErrorMessage";
import WorkflowPipeline from "./components/WorkflowPipeline";

export default function PurchaseDashboard() {
  const { data, isLoading, error } = useMeta();

  if (isLoading) {
    return <Loading />;
  }

  if (error || !data) {
    return <ErrorMessage message="Unable to load workflow status" />;
  }

  return (
    <>
      <Typography variant="h4">
        Purchase Workflow Dashboard
      </Typography>

      <WorkflowPipeline
        purchaseList={data.statuses.purchase_list}
        purchaseChecklist={data.statuses.purchase_checklist}
      />
    </>
  );
}
