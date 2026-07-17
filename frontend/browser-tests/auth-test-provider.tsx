import { PropsWithChildren } from "react";

import {
  AuthContext,
  AuthContextValue,
} from "@/features/auth/providers/AuthProvider";

const value: AuthContextValue = {
  user: {
    id: 1,
    email: "admin@tourhub.local",
    display_name: "Локальный администратор",
    role: "administrator",
    is_active: true,
    created_at: "2026-07-18T00:00:00",
  },
  bootstrapRequired: false,
  isLoading: false,
  refresh: async () => undefined,
  bootstrap: async () => undefined,
  login: async () => undefined,
  logout: async () => undefined,
};

export default function AuthTestProvider({ children }: PropsWithChildren) {
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
