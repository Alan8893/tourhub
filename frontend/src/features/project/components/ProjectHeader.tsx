import { Typography } from "@mui/material";

import type { Project } from "../api/projectApi";

interface Props {
  project: Project;
}

export default function ProjectHeader({ project }: Props) {
  return (
    <>
      <Typography variant="h4">{project.name}</Typography>
      <Typography variant="body1">
        Participants: {project.participants} · Days: {project.days} · Status: {project.status}
      </Typography>
    </>
  );
}
