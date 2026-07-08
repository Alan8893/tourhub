import { Alert, Box, CircularProgress, Typography } from "@mui/material";

import { useMeta } from "../features/meta/hooks/useMeta";

export default function PurchaseDashboardPage() {
  const { data, isLoading, error } = useMeta();

  if (isLoading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Alert severity="error">Failed to load TourHub API metadata</Alert>;
  }

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h4">Purchase Dashboard</Typography>

      <Typography sx={{ mt: 2 }}>
        Application: {data?.name}
      </Typography>

      <Typography>
        API version: {data?.api_version}
      </Typography>

      <Typography sx={{ mt: 2 }}>
        Purchase List statuses: {data?.statuses.purchase_list.join(", ")}
      </Typography>

      <Typography>
        Purchase Checklist statuses: {data?.statuses.purchase_checklist.join(", ")}
      </Typography>
    </Box>
  );
}
