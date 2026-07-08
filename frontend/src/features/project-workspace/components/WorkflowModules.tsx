import { Grid } from "@mui/material";

import ModuleCard from "./ModuleCard";

const modules = [
  {
    title: "Meal Plan",
    description: "Manage hike nutrition planning.",
  },
  {
    title: "Shopping List",
    description: "Prepare products required for the trip.",
  },
  {
    title: "Packaging",
    description: "Organize products and equipment packages.",
  },
  {
    title: "Purchase Checklist",
    description: "Track purchase completion.",
  },
  {
    title: "Documents",
    description: "Generate expedition documents.",
  },
];

export default function WorkflowModules() {
  return (
    <Grid container spacing={2} sx={{ mt: 2 }}>
      {modules.map((module) => (
        <Grid item xs={12} md={4} key={module.title}>
          <ModuleCard {...module} />
        </Grid>
      ))}
    </Grid>
  );
}
