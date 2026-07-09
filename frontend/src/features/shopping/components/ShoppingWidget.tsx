import { Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function ShoppingWidget() {
  const { preparationResult } = useProjectWorkflow();

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Shopping List</Typography>
        <Typography>
          {preparationResult?.purchase_list_id
            ? `Purchase list: ${preparationResult.purchase_list_id}`
            : "Prepare products required for the trip."}
        </Typography>
      </CardContent>
    </Card>
  );
}
