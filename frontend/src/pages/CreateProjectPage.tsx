import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useCreateProject } from "../features/project/hooks/useCreateProject";

export default function CreateProjectPage() {
  const navigate = useNavigate();
  const createProject = useCreateProject();

  const [name, setName] = useState("");
  const [participants, setParticipants] = useState(1);
  const [days, setDays] = useState(1);

  async function submit(event: FormEvent) {
    event.preventDefault();

    const project = await createProject.mutateAsync({
      name,
      participants,
      days,
    });

    navigate(`/projects/${project.id}`);
  }

  return (
    <form onSubmit={submit}>
      <h1>Create Project</h1>

      <input
        value={name}
        onChange={(event) => setName(event.target.value)}
        placeholder="Project name"
      />

      <input
        type="number"
        value={participants}
        onChange={(event) => setParticipants(Number(event.target.value))}
        min={1}
      />

      <input
        type="number"
        value={days}
        onChange={(event) => setDays(Number(event.target.value))}
        min={1}
      />

      <button type="submit" disabled={createProject.isPending}>
        Create
      </button>
    </form>
  );
}
