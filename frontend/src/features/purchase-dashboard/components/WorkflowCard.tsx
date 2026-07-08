import { Card, CardContent, Typography } from "@mui/material";

interface Props {
  title: string;
  statuses: string[];
}

export default function WorkflowCard({ title, statuses }: Props) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{title}</Typography>

        {statuses.map((status) => (
          <Typography key={status}>{status}</Typography>
        ))}
      </CardContent>
    </Card>
  );
}
