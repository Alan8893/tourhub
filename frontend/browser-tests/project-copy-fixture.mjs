import { createServer } from "node:http";

export const projectCopyRequests = [];

export const projectCopySource = {
  id: 88,
  name: "Кольский маршрут",
  participants: 12,
  days: 5,
  start_date: "2026-08-01",
  first_meal: "dinner",
  last_meal: "lunch",
  recipe_generation_mode: "club_and_personal",
  status: "completed",
  owner_user_id: 1,
  owner_display_name: "Иван Владелец",
  capabilities: {
    can_view: true,
    can_manage_project: false,
    can_manage_team: false,
    can_transfer_ownership: false,
    can_edit_menu: false,
    can_operate_shopping: false,
    can_operate_equipment: false,
    can_generate_documents: true,
    can_delete: true,
  },
};

export const projectCopySourceSnapshot = JSON.stringify(projectCopySource);

function sendJson(response, payload, statusCode = 200) {
  response.statusCode = statusCode;
  response.setHeader("content-type", "application/json; charset=utf-8");
  response.end(JSON.stringify(payload));
}

async function readJson(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  const text = Buffer.concat(chunks).toString("utf-8");
  return text ? JSON.parse(text) : null;
}

export function startProjectCopyApi(port = 18119) {
  projectCopyRequests.length = 0;
  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);

    if (request.method === "GET" && url.pathname === "/api/v1/projects/88") {
      projectCopyRequests.push({ method: request.method, path: url.pathname, body: null });
      sendJson(response, projectCopySource);
      return;
    }

    if (request.method === "POST" && url.pathname === "/api/v1/projects/88/copy") {
      const body = await readJson(request);
      projectCopyRequests.push({ method: request.method, path: url.pathname, body });
      await new Promise((resolve) => setTimeout(resolve, 250));
      sendJson(response, {
        project_id: 501,
        meal_plan_id: "meal-plan-501",
        copied_slot_count: 4,
        copied_assignment_count: 7,
        skipped_assignment_count: 1,
        warnings: [
          "День 2, lunch: назначение «Архивное блюдо» пропущено.",
        ],
      });
      return;
    }

    sendJson(response, { detail: `Unhandled mock path: ${url.pathname}` }, 404);
  });

  return {
    listen: () =>
      new Promise((resolve, reject) => {
        server.once("error", reject);
        server.listen(port, "127.0.0.1", resolve);
      }),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
