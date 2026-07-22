import { createServer } from "node:http";

function json(response, statusCode, body) {
  response.statusCode = statusCode;
  response.setHeader("content-type", "application/json");
  response.end(JSON.stringify(body));
}

export function createProjectTeamAccessMockApi(port) {
  const requests = [];
  const currentUser = {
    id: 2,
    email: "collaborator@tourhub.local",
    display_name: "Анна Приглашённая",
    role: "verified_instructor",
    is_active: true,
    created_at: "2026-07-20T00:00:00",
  };
  const collaboratorCapabilities = {
    can_view: true,
    can_manage_project: false,
    can_manage_team: false,
    can_transfer_ownership: false,
    can_edit_menu: false,
    can_operate_shopping: true,
    can_operate_equipment: true,
    can_generate_documents: true,
    can_delete: false,
  };
  const completedCapabilities = {
    ...collaboratorCapabilities,
    can_operate_shopping: false,
    can_operate_equipment: false,
  };
  const activeProject = {
    id: 77,
    name: "Доступный поход",
    participants: 14,
    days: 6,
    start_date: "2026-08-12",
    first_meal: "dinner",
    last_meal: "breakfast",
    recipe_generation_mode: "club_only",
    status: "prepared",
    owner_user_id: 1,
    owner_display_name: "Иван Владелец",
    capabilities: collaboratorCapabilities,
  };
  const completedProject = {
    ...activeProject,
    id: 88,
    name: "Завершённый поход",
    status: "completed",
    capabilities: completedCapabilities,
  };
  const team = {
    owner: {
      id: 1,
      email: "owner@tourhub.local",
      display_name: "Иван Владелец",
      phone: "+79991112233",
      telegram_url: "https://t.me/ivan_owner",
      max_url: "https://max.ru/ivan-owner",
      vk_url: "https://vk.com/ivan-owner",
      role: "instructor",
      is_active: true,
      project_role: "owner",
    },
    instructors: [
      {
        id: 2,
        email: currentUser.email,
        display_name: currentUser.display_name,
        phone: "+79994445566",
        telegram_url: "https://t.me/anna_guide",
        max_url: null,
        vk_url: null,
        role: currentUser.role,
        is_active: true,
        project_role: "additional_instructor",
      },
    ],
  };
  const mealPlan = {
    id: "meal-plan-77",
    project_id: 77,
    name: "Меню: Доступный поход",
    participants: 14,
    days_count: 6,
    items: [],
    meals: [
      {
        id: "slot-1",
        day_number: 1,
        meal_type: "dinner",
        dishes: [
          {
            id: "slot-dish-1",
            dish_id: "dish-1",
            dish_name: "Плов",
            recipe_id: "recipe-1",
            recipe_name: "Плов походный",
          },
        ],
      },
    ],
    warnings: [],
  };

  const server = createServer((request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    requests.push({ method: request.method ?? "GET", path: url.pathname });

    if (request.method === "GET" && url.pathname === "/api/v1/auth/bootstrap-status") {
      return json(response, 200, { bootstrap_required: false });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/auth/me") {
      return json(response, 200, { user: currentUser });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/projects") {
      return json(response, 200, { items: [completedProject, activeProject] });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/projects/77") {
      return json(response, 200, activeProject);
    }
    if (request.method === "GET" && url.pathname === "/api/v1/projects/77/team") {
      return json(response, 200, team);
    }
    if (request.method === "GET" && url.pathname === "/api/v1/projects/77/preparation") {
      return json(response, 200, {
        project_id: 77,
        meal_plan_id: "meal-plan-77",
        purchase_list_id: "purchase-list-77",
        purchase_checklist_id: "checklist-77",
        equipment_list_id: "equipment-list-77",
      });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/meal-plans/project/77") {
      return json(response, 200, mealPlan);
    }
    if (
      request.method === "GET" &&
      url.pathname === "/api/v1/projects/77/team/1/vcard"
    ) {
      response.statusCode = 200;
      response.setHeader("content-type", "text/vcard; charset=utf-8");
      response.end("BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Иван Владелец\r\nEND:VCARD\r\n");
      return;
    }
    if (request.method === "GET" && url.pathname === "/api/v1/club-settings") {
      return json(response, 200, { club_name: "Турклуб Полюс", logo_data_url: null });
    }

    json(response, 404, { detail: `Unhandled mock path: ${url.pathname}` });
  });

  return {
    requests,
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
