import { Card, CardContent, Typography } from "@mui/material";

export default function ShoppingWidget() {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Shopping List</Typography>
        <Typography>Prepare products required for the trip.</Typography>
      </CardContent>
    </Card>
  );
}
