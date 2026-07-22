import { createServer } from "node:http";

function json(response, statusCode, body) {
  response.statusCode = statusCode;
  response.setHeader("content-type", "application/json");
  response.end(JSON.stringify(body));
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  const payload = Buffer.concat(chunks).toString("utf8");
  return payload ? JSON.parse(payload) : undefined;
}

const ownerCapabilities = {
  can_view: true,
  can_manage_project: true,
  can_manage_team: true,
  can_transfer_ownership: true,
  can_edit_menu: true,
  can_operate_shopping: true,
  can_operate_equipment: true,
  can_generate_documents: true,
  can_delete: true,
};

export function createGuidedReleaseMockApi(port) {
  const requests = [];
  let mealGenerated = false;
  let prepared = false;
  let project = {
    id: 77,
    name: "Карелия 2026",
    participants: 8,
    days: 3,
    start_date: null,
    first_meal: "dinner",
    last_meal: "dinner",
    recipe_generation_mode: "club_only",
    status: "draft",
    owner_user_id: 1,
    owner_display_name: "Тестовый инструктор",
    capabilities: ownerCapabilities,
  };
  const currentUser = {
    id: 1,
    email: "instructor@tourhub.local",
    display_name: "Тестовый инструктор",
    role: "instructor",
    is_active: true,
    created_at: "2026-07-18T00:00:00",
  };
  const projectTeam = {
    owner: {
      id: 1,
      email: "instructor@tourhub.local",
      display_name: "Тестовый инструктор",
      phone: "+79991234567",
      telegram_url: "https://t.me/test_guide",
      max_url: "https://max.ru/test-guide",
      vk_url: "https://vk.com/test-guide",
      role: "instructor",
      is_active: true,
      project_role: "owner",
    },
    instructors: [],
  };
  const mealPlan = {
    id: "meal-plan-77",
    project_id: 77,
    name: "Меню: Карелия 2026",
    participants: 8,
    days_count: 3,
    items: [],
    meals: [
      {
        id: "legacy:1:dinner",
        day_number: 1,
        meal_type: "dinner",
        dishes: [
          {
            id: "legacy-dish-1",
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

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = ["POST", "PUT", "PATCH"].includes(request.method ?? "")
      ? await readBody(request)
      : undefined;
    requests.push({ method: request.method ?? "GET", path: url.pathname, body });

    if (request.method === "GET" && url.pathname === "/api/v1/auth/bootstrap-status") {
      return json(response, 200, { bootstrap_required: false });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/auth/me") {
      return json(response, 200, { user: currentUser });
    }
    if (request.method === "POST" && url.pathname === "/api/v1/projects") {
      project = {
        ...project,
        ...body,
        start_date: body.start_date ?? null,
        owner_user_id: currentUser.id,
        owner_display_name: currentUser.display_name,
        capabilities: ownerCapabilities,
      };
      return json(response, 200, project);
    }
    if (request.method === "GET" && url.pathname === "/api/v1/projects/77") {
      return json(response, 200, project);
    }
    if (request.method === "GET" && url.pathname === "/api/v1/projects/77/team") {
      return json(response, 200, projectTeam);
    }
    if (
      request.method === "GET" &&
      url.pathname === "/api/v1/projects/77/team/candidates"
    ) {
      return json(response, 200, []);
    }
    if (request.method === "GET" && url.pathname === "/api/v1/projects/77/preparation") {
      return json(response, 200, {
        project_id: 77,
        meal_plan_id: mealGenerated ? "meal-plan-77" : "",
        purchase_list_id: prepared ? "purchase-list-77" : "",
        purchase_checklist_id: prepared ? "checklist-77" : "",
        equipment_list_id: prepared ? "equipment-list-77" : "",
      });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/meal-plans/project/77") {
      return json(response, mealGenerated ? 200 : 404, mealGenerated ? mealPlan : { detail: "not found" });
    }
    if (request.method === "POST" && url.pathname === "/api/v1/meal-plans/project/77/generate") {
      mealGenerated = true;
      return json(response, 200, mealPlan);
    }
    if (request.method === "POST" && url.pathname === "/api/v1/projects/77/prepare") {
      prepared = true;
      return json(response, 200, {
        project_id: 77,
        meal_plan_id: "meal-plan-77",
        purchase_list_id: "purchase-list-77",
        purchase_checklist_id: "checklist-77",
        equipment_list_id: "equipment-list-77",
      });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/purchase-lists/project/77") {
      return prepared
        ? json(response, 200, {
            id: "purchase-list-77",
            project_id: 77,
            meal_plan_id: "meal-plan-77",
            status: "draft",
            responsible_person: null,
            items: [
              {
                id: "purchase-item-1",
                product_id: "product-1",
                product_name: "Рис",
                required_quantity: 2,
                required_unit: "кг",
                package_size: 1,
                package_unit: "кг",
                packages_count: 2,
                purchase_quantity: 2,
                surplus_quantity: 0,
              },
            ],
          })
        : json(response, 404, { detail: "not found" });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/purchase-checklists/project/77") {
      return prepared
        ? json(response, 200, {
            id: "checklist-77",
            project_id: 77,
            meal_plan_id: "meal-plan-77",
            status: "draft",
            items: [
              {
                id: "checklist-item-1",
                product_id: "product-1",
                product_name: "Рис",
                required_quantity: 2,
                purchased_quantity: 0,
                remaining_quantity: 2,
                unit: "кг",
                is_checked: false,
              },
            ],
          })
        : json(response, 404, { detail: "not found" });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/equipment-lists/project/77") {
      return prepared
        ? json(response, 200, {
            id: "equipment-list-77",
            project_id: 77,
            meal_plan_id: "meal-plan-77",
            status: "prepared",
            items: [
              {
                id: "equipment-item-1",
                equipment_name: "Котёл",
                required_quantity: 2,
                calculated_quantity: 2,
                is_manual: false,
                is_overridden: false,
              },
            ],
          })
        : json(response, 404, { detail: "not found" });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/club-settings") {
      return json(response, 200, { club_name: "Турклуб Полюс", logo_data_url: null });
    }
    if (request.method === "GET" && url.pathname === "/api/v1/projects/77/documents/package") {
      response.statusCode = 200;
      response.setHeader("content-type", "application/zip");
      response.end(Buffer.from("guided-release-package"));
      return;
    }

    json(response, 404, { detail: `Unhandled mock path: ${url.pathname}` });
  });

  return {
    requests,
    listen: () => new Promise((resolve, reject) => {
      server.once("error", reject);
      server.listen(port, "127.0.0.1", resolve);
    }),
    close: () => new Promise((resolve) => {
      server.closeAllConnections();
      server.close(resolve);
    }),
  };
}
