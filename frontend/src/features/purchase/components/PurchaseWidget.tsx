import { Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function PurchaseWidget() {
  const { preparationResult } = useProjectWorkflow();

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Purchase Checklist</Typography>
        <Typography>
          {preparationResult?.purchase_checklist_id
            ? `Checklist: ${preparationResult.purchase_checklist_id}`
            : "Track purchase completion."}
        </Typography>
      </CardContent>
    </Card>
  );
}
