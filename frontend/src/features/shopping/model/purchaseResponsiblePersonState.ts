export const responsiblePersonMaxLength = 255;

export function normalizeResponsiblePerson(value: string): string | null {
  const normalized = value.trim();
  return normalized.length > 0 ? normalized : null;
}

export function isResponsiblePersonValid(value: string): boolean {
  return value.length <= responsiblePersonMaxLength;
}

export function getResponsiblePersonSuccessMessage(value: string): string {
  return normalizeResponsiblePerson(value)
    ? "Ответственный сохранён."
    : "Ответственный удалён.";
}
