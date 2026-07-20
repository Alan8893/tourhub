import { createServer } from "node:http";

export const auditRequests = [];

const events = [
  {
    id: 8,
    actor_user_id: 1,
    actor_display_name: "Анна Администратор",
    actor_email: "admin@tourhub.local",
    actor_role: "administrator",
    action: "mail_test_message_delivery",
    entity_type: "mail",
    entity_id: "smtp",
    before_data: null,
    after_data: {
      status: "sent",
      attempts: 1,
      recipient: "operator@tourhub.local",
    },
    context_data: {
      settings_version: 4,
      security_mode: "starttls",
      authentication_configured: true,
    },
    created_at: "2026-07-20T08:58:00Z",
  },
  {
    id: 7,
    actor_user_id: 1,
    actor_display_name: "Анна Администратор",
    actor_email: "admin@tourhub.local",
    actor_role: "administrator",
    action: "mail_settings_updated",
    entity_type: "system_settings",
    entity_id: "mail",
    before_data: {
      version: 3,
      smtp_port: 587,
    },
    after_data: {
      version: 4,
      smtp_port: 2525,
    },
    context_data: {
      section: "mail",
      changed_fields: ["smtp_port"],
      previous_version: 3,
      settings_version: 4,
    },
    created_at: "2026-07-20T08:57:00Z",
  },
  {
    id: 6,
    actor_user_id: 1,
    actor_display_name: "Анна Администратор",
    actor_email: "admin@tourhub.local",
    actor_role: "administrator",
    action: "meal_slot_dish_replaced",
    entity_type: "meal_slot",
    entity_id: "slot-dinner-42",
    before_data: {
      meal_type: "dinner",
      dish_count: 1,
      dishes: [{ dish_id: "dish-rice", recipe_id: "recipe-rice", order: 0 }],
    },
    after_data: {
      meal_type: "dinner",
      dish_count: 1,
      dishes: [{ dish_id: "dish-beans", recipe_id: "recipe-beans", order: 0 }],
    },
    context_data: {
      project_id: 42,
      meal_plan_id: "plan-42",
      previous_dish_id: "dish-rice",
      dish_id: "dish-beans",
    },
    created_at: "2026-07-19T08:55:00Z",
  },
  {
    id: 5,
    actor_user_id: 1,
    actor_display_name: "Анна Администратор",
    actor_email: "admin@tourhub.local",
    actor_role: "administrator",
    action: "meal_plan_generated",
    entity_type: "meal_plan",
    entity_id: "plan-42",
    before_data: null,
    after_data: {
      participants: 12,
      days_count: 3,
      slot_count: 10,
      slot_dish_count: 10,
      manual_slot_count: 0,
      warnings: [],
    },
    context_data: {
      project_id: 42,
      generation_kind: "initial",
      recipe_generation_mode: "club_only",
    },
    created_at: "2026-07-19T08:50:00Z",
  },
  {
    id: 4,
    actor_user_id: 1,
    actor_display_name: "Анна Администратор",
    actor_email: "admin@tourhub.local",
    actor_role: "administrator",
    action: "project_prepared",
    entity_type: "project",
    entity_id: "42",
    before_data: {
      purchase_list_count: 0,
      purchase_checklist_count: 0,
      equipment_list_id: null,
    },
    after_data: {
      purchase_list_count: 1,
      purchase_checklist_count: 1,
      equipment_list_id: "equipment-42",
    },
    context_data: {
      meal_plan_id: "plan-42",
      purchase_list_id: "purchase-42",
      purchase_checklist_id: "checklist-42",
      equipment_list_id: "equipment-42",
    },
    created_at: "2026-07-19T08:40:00Z",
  },
  {
    id: 3,
    actor_user_id: 1,
    actor_display_name: "Анна Администратор",
    actor_email: "admin@tourhub.local",
    actor_role: "administrator",
    action: "recipe_rejected",
    entity_type: "recipe",
    entity_id: "recipe-17",
    before_data: { lifecycle_status: "submitted", review_comment: null },
    after_data: {
      lifecycle_status: "rejected",
      review_comment: "Уточните технологию приготовления.",
    },
    context_data: { recipe_name: "Плов походный" },
    created_at: "2026-07-19T08:30:00Z",
  },
  {
    id: 2,
    actor_user_id: 1,
    actor_display_name: "Анна Администратор",
    actor_email: "admin@tourhub.local",
    actor_role: "administrator",
    action: "user_role_changed",
    entity_type: "user",
    entity_id: "8",
    before_data: { role: "instructor", is_active: true },
    after_data: { role: "verified_instructor", is_active: true },
    context_data: { changed_fields: ["role"] },
    created_at: "2026-07-19T08:20:00Z",
  },
];

export function startAuditLogApi() {
  auditRequests.length = 0;
  const server = createServer((request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    auditRequests.push({
      method: request.method,
      path: url.pathname,
      query: Object.fromEntries(url.searchParams.entries()),
    });
    response.setHeader("content-type", "application/json");

    if (request.method === "GET" && url.pathname === "/api/v1/audit/events") {
      const entityType = url.searchParams.get("entity_type");
      const action = url.searchParams.get("action");
      const items = events.filter(
        (event) =>
          (!entityType || event.entity_type === entityType) &&
          (!action || event.action === action),
      );
      response.end(
        JSON.stringify({
          items,
          total: items.length,
          limit: Number(url.searchParams.get("limit") ?? 50),
          offset: Number(url.searchParams.get("offset") ?? 0),
        }),
      );
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18095, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
