import { Navigate, RouteObject } from "react-router-dom";

import AppLayout from "../layout/AppLayout";
import ProjectWorkspacePage from "../../pages/ProjectWorkspacePage";
import CreateProjectPage from "../../pages/CreateProjectPage";

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
