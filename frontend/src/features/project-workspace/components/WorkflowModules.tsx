import { Grid } from "@mui/material";

import { DocumentsWidget } from "@/features/documents";
import CampInventoryWidget from "@/features/equipment/components/CampInventoryWidget";
import { MealPlanWidget } from "@/features/meal-plan";
import { PurchaseWidget } from "@/features/purchase";
import { ShoppingWidget } from "@/features/shopping";
import { useModuleVisibility } from "@/features/system-settings/providers/ModuleVisibilityProvider";

export default function WorkflowModules() {
  const { settings } = useModuleVisibility();

  return (
    <Grid container spacing={2} sx={{ mt: 2 }}>
      <Grid item xs={12}>
        <MealPlanWidget />
      </Grid>

      {settings.shopping_visible && (
        <>
          <Grid item xs={12} md={6}>
            <ShoppingWidget />
          </Grid>

          <Grid item xs={12} md={6}>
            <PurchaseWidget />
          </Grid>
        </>
      )}

      {settings.equipment_visible && (
        <Grid item xs={12}>
          <CampInventoryWidget />
        </Grid>
      )}

      {settings.documents_visible && (
        <Grid item xs={12}>
          <DocumentsWidget />
        </Grid>
      )}
    </Grid>
  );
}
