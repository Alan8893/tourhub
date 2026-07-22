import type { AccountSession } from "../api/accountApi";

export function canRevokeAccountSession(session: AccountSession): boolean {
  return !session.is_current;
}

export function withoutAccountSession(
  sessions: AccountSession[],
  sessionId: number,
): AccountSession[] {
  return sessions.filter((session) => session.id !== sessionId);
}

export function formatAccountSessionTime(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
