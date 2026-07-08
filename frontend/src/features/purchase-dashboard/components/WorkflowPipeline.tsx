import { Grid } from "@mui/material";

import WorkflowCard from "./WorkflowCard";

interface Props {
  purchaseList: string[];
  purchaseChecklist: string[];
}

export default function WorkflowPipeline({
  purchaseList,
  purchaseChecklist,
}: Props) {
  return (
    <Grid container spacing={2} sx={{ mt: 2 }}>
      <Grid item xs={12} md={6}>
        <WorkflowCard
          title="Purchase List"
          statuses={purchaseList}
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <WorkflowCard
          title="Purchase Checklist"
          statuses={purchaseChecklist}
        />
      </Grid>
    </Grid>
  );
}
