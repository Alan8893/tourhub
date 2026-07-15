import { Grid } from "@mui/material";

import { DocumentsWidget } from "@/features/documents";
import { MealPlanWidget } from "@/features/meal-plan";
import { PurchaseWidget } from "@/features/purchase";
import { ShoppingWidget } from "@/features/shopping";

export default function WorkflowModules() {
  return (
    <Grid container spacing={2} sx={{ mt: 2 }}>
      <Grid item xs={12}>
        <MealPlanWidget />
      </Grid>

      <Grid item xs={12} md={6}>
        <ShoppingWidget />
      </Grid>

      <Grid item xs={12} md={6}>
        <PurchaseWidget />
      </Grid>

      <Grid item xs={12}>
        <DocumentsWidget />
      </Grid>
    </Grid>
  );
}
