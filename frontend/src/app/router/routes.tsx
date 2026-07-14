import { Navigate, RouteObject } from "react-router-dom";

import AppLayout from "../layout/AppLayout";
import CreateProjectPage from "../../pages/CreateProjectPage";
import ProjectWorkspacePage from "../../pages/ProjectWorkspacePage";
import RecipesPage from "../../pages/RecipesPage";

export const routes: RouteObject[] = [
  {
    element: <AppLayout />,
    children: [
      {
        path: "/",
        element: <Navigate to="/projects/new" replace />,
      },
      {
        path: "/projects/new",
        element: <CreateProjectPage />,
      },
      {
        path: "/projects",
        element: <ProjectWorkspacePage />,
      },
      {
        path: "/projects/:id",
        element: <ProjectWorkspacePage />,
      },
      {
        path: "/recipes",
        element: <RecipesPage />,
      },
      {
        path: "/recipes/:id",
        element: <RecipesPage />,
      },
      {
        path: "/login",
        element: <div>Login</div>,
      },
      {
        path: "/dashboard",
        element: <div>Dashboard</div>,
      },
    ],
  },
];
