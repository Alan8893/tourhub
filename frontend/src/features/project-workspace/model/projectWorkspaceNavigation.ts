export const PROJECT_WORKSPACE_SECTIONS = [
  { id: "overview", label: "Обзор", icon: "⌂" },
  { id: "menu", label: "Меню", icon: "♨" },
  { id: "shopping", label: "Закупка", icon: "🛒" },
  { id: "equipment", label: "Оборудование", icon: "▣" },
  { id: "documents", label: "Документы", icon: "▤" },
] as const;

export type ProjectWorkspaceSection =
  (typeof PROJECT_WORKSPACE_SECTIONS)[number]["id"];

const SECTION_IDS = new Set<string>(
  PROJECT_WORKSPACE_SECTIONS.map((section) => section.id),
);

export function normalizeProjectWorkspaceSection(
  value: string | undefined,
): ProjectWorkspaceSection {
  return value && SECTION_IDS.has(value)
    ? (value as ProjectWorkspaceSection)
    : "overview";
}

export function buildProjectWorkspacePath(
  projectId: number,
  section: ProjectWorkspaceSection,
): string {
  const basePath = `/projects/${projectId}`;
  return section === "overview" ? basePath : `${basePath}/${section}`;
}
