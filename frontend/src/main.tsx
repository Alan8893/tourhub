import React from "react";
import ReactDOM from "react-dom/client";

import { CssBaseline } from "@mui/material";
import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";

import App from "./app/App";
import { queryClient } from "./app/providers/queryClient";
import AuthProvider from "./features/auth/providers/AuthProvider";
import AppearanceProvider from "./features/system-settings/providers/AppearanceProvider";
import ModuleVisibilityProvider from "./features/system-settings/providers/ModuleVisibilityProvider";
import ErrorBoundary from "./shared/ui/ErrorBoundary";

const INVITATION_PATH = "/accept-invitation";

function prepareInvitationFragment(): void {
  if (window.location.pathname !== INVITATION_PATH || !window.location.hash) return;
  const fragment = new URLSearchParams(window.location.hash.replace(/^#/, ""));
  const code = fragment.get("token")?.trim();
  if (!code || new URLSearchParams(window.location.search).has("token")) return;

  window.history.replaceState(
    window.history.state,
    "",
    `${INVITATION_PATH}?token=${encodeURIComponent(code)}`,
  );
  window.setTimeout(() => {
    if (window.location.pathname === INVITATION_PATH) {
      window.history.replaceState(window.history.state, "", INVITATION_PATH);
    }
  }, 2000);
}

prepareInvitationFragment();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider>
            <AppearanceProvider>
              <ModuleVisibilityProvider>
                <CssBaseline />
                <App />
              </ModuleVisibilityProvider>
            </AppearanceProvider>
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>,
);
