import {
  PropsWithChildren,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { SESSION_INVALIDATED_EVENT } from "@/shared/api/sessionEvents";
import {
  AuthUser,
  bootstrapAdministrator,
  getBootstrapStatus,
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
} from "../api/authApi";

export interface AuthContextValue {
  user: AuthUser | null;
  bootstrapRequired: boolean;
  isLoading: boolean;
  refresh: () => Promise<void>;
  bootstrap: (payload: {
    email: string;
    display_name: string;
    password: string;
  }) => Promise<void>;
  login: (payload: { email: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export default function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [bootstrapRequired, setBootstrapRequired] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const [required, currentUser] = await Promise.all([
        getBootstrapStatus(),
        getCurrentUser(),
      ]);
      setBootstrapRequired(required);
      setUser(currentUser);
    } catch {
      setBootstrapRequired(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const handleSessionInvalidated = () => {
      setUser(null);
      setIsLoading(false);
    };
    window.addEventListener(SESSION_INVALIDATED_EVENT, handleSessionInvalidated);
    return () => window.removeEventListener(SESSION_INVALIDATED_EVENT, handleSessionInvalidated);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const bootstrap = useCallback(
    async (payload: { email: string; display_name: string; password: string }) => {
      const created = await bootstrapAdministrator(payload);
      setUser(created);
      setBootstrapRequired(false);
    },
    [],
  );

  const login = useCallback(async (payload: { email: string; password: string }) => {
    setUser(await loginRequest(payload));
    setBootstrapRequired(false);
  }, []);

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      bootstrapRequired,
      isLoading,
      refresh,
      bootstrap,
      login,
      logout,
    }),
    [bootstrap, bootstrapRequired, isLoading, login, logout, refresh, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useOptionalAuth(): AuthContextValue | null {
  return useContext(AuthContext);
}

export function useAuth(): AuthContextValue {
  const context = useOptionalAuth();
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
