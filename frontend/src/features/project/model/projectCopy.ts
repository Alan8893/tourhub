import type { CreateProjectRequest, Project, ProjectCopyResponse } from "../api/projectApi";

export function buildProjectCopyDefaults(source: Project): CreateProjectRequest {
  return {
    name: `${source.name} — копия`,
    participants: source.participants,
    days: source.days,
    start_date: source.start_date ?? undefined,
    first_meal: source.first_meal ?? undefined,
    last_meal: source.last_meal ?? undefined,
    recipe_generation_mode: source.recipe_generation_mode,
  };
}

export function projectCopySummary(result: ProjectCopyResponse): string {
  const skipped = result.skipped_assignment_count
    ? ` Пропущено назначений: ${result.skipped_assignment_count}.`
    : "";
  return `Скопировано слотов: ${result.copied_slot_count}, назначений: ${result.copied_assignment_count}.${skipped}`;
}
