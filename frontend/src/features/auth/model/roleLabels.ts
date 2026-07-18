import type { UserRole } from "../api/authApi";

const USER_ROLE_LABELS: Record<UserRole, string> = {
  administrator: "Администратор",
  instructor: "Инструктор",
  verified_instructor: "Проверенный инструктор",
};

export function userRoleLabel(role: UserRole): string {
  return USER_ROLE_LABELS[role];
}
