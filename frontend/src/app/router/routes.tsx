import { Navigate, RouteObject } from "react-router-dom";

import AppLayout from "../layout/AppLayout";
import CatalogImportPage from "../../pages/CatalogImportPage";
import CreateProjectPage from "../../pages/CreateProjectPage";
import DishesWorkspacePage from "../../pages/DishesWorkspacePage";
import ProjectsPage from "../../pages/ProjectsPage";
import ProjectWorkspacePage from "../../pages/ProjectWorkspacePage";
import RecipesPage from "../../pages/RecipesPage";
import SettingsPage from "../../pages/SettingsPage";

export const routes: RouteObject[] = [
  {
    element: <AppLayout />,
    children: [
      { path: "/", element: <Navigate to="/projects" replace /> },
      { path: "/projects/new", element: <CreateProjectPage /> },
      { path: "/projects", element: <ProjectsPage /> },
      { path: "/projects/:id", element: <ProjectWorkspacePage /> },
      { path: "/recipes", element: <RecipesPage /> },
      { path: "/recipes/:id", element: <RecipesPage /> },
      { path: "/dishes", element: <DishesWorkspacePage /> },
      { path: "/dishes/:id", element: <DishesWorkspacePage /> },
      { path: "/catalog-import", element: <CatalogImportPage /> },
      { path: "/settings", element: <SettingsPage /> },
      { path: "/login", element: <div>Login</div> },
      { path: "/dashboard", element: <div>Dashboard</div> },
    ],
  },
];
