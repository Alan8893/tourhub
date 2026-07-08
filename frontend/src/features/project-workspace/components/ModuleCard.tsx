import { Card, CardContent, Typography } from "@mui/material";

interface Props {
  title: string;
  description: string;
}

export default function ModuleCard({ title, description }: Props) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{title}</Typography>
        <Typography variant="body2">{description}</Typography>
      </CardContent>
    </Card>
  );
}
