import { createServer } from "node:http";

export const requests = [];

const editableRecipe = {
  id: "recipe-editable",
  name: "Каша для редактирования",
  scope: "personal",
  owner_user_id: 2,
  owner_display_name: "Проверяющий",
  is_owned_by_current_user: true,
  lifecycle_status: "draft",
  submitted_by_user_id: null,
  submitted_by_display_name: null,
  submitted_at: null,
  reviewed_by_user_id: null,
  reviewed_by_display_name: null,
  reviewed_at: null,
  review_comment: null,
  can_edit: true,
  can_archive: true,
  can_restore: false,
  can_delete: true,
  can_submit: true,
  can_publish: false,
  can_reject: false,
  is_archived: false,
  component_count: 1,
  note_count: 0,
  components: [
    {
      id: "component-editable",
      component_type: "base",
      amount: 80,
      unit: "gram",
      calculation_type: "per_person",
      people_count: null,
      product: {
        id: "product-editable",
        name: "Гречка",
        category: "Крупы",
        unit: "gram",
        package_size: 800,
      },
    },
  ],
  notes: [],
};

const submittedRecipe = {
  id: "recipe-submitted",
  name: "Каша на проверку",
  scope: "personal",
  owner_user_id: 7,
  owner_display_name: "Автор рецепта",
  is_owned_by_current_user: false,
  lifecycle_status: "submitted",
  submitted_by_user_id: 7,
  submitted_by_display_name: "Автор рецепта",
  submitted_at: "2026-07-18T12:00:00+00:00",
  reviewed_by_user_id: null,
  reviewed_by_display_name: null,
  reviewed_at: null,
  review_comment: null,
  can_edit: false,
  can_archive: false,
  can_restore: false,
  can_delete: false,
  can_submit: false,
  can_publish: true,
  can_reject: true,
  is_archived: false,
  component_count: 1,
  note_count: 1,
  components: [
    {
      id: "component-1",
      component_type: "base",
      amount: 80,
      unit: "gram",
      calculation_type: "per_person",
      people_count: null,
      product: {
        id: "product-1",
        name: "Гречка",
        category: "Крупы",
        unit: "gram",
        package_size: 800,
      },
    },
  ],
  notes: [
    {
      id: "note-1",
      type: "cooking_tip",
      text: "Промыть крупу.",
      priority: 10,
      created_at: "2026-07-18T11:00:00+00:00",
    },
  ],
};

let pending = true;

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  const content = Buffer.concat(chunks).toString("utf8");
  return content ? JSON.parse(content) : undefined;
}

function listItem(recipe) {
  const { components, notes, ...item } = recipe;
  return item;
}

export function startRecipeModerationApi() {
  requests.length = 0;
  pending = true;
  editableRecipe.components[0].product = {
    id: "product-editable",
    name: "Гречка",
    category: "Крупы",
    unit: "gram",
    package_size: 800,
  };
  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = ["POST", "PUT", "PATCH"].includes(request.method ?? "")
      ? await readBody(request)
      : undefined;
    requests.push({ method: request.method, path: url.pathname, query: url.search, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/recipes" && request.method === "GET") {
      const moderation = url.searchParams.get("view") === "moderation";
      response.end(
        JSON.stringify({
          items: moderation
            ? pending
              ? [listItem(submittedRecipe)]
              : []
            : [listItem(editableRecipe)],
        }),
      );
      return;
    }

    if (url.pathname === `/api/v1/recipes/${editableRecipe.id}` && request.method === "GET") {
      response.end(JSON.stringify(editableRecipe));
      return;
    }

    if (url.pathname === `/api/v1/recipes/${submittedRecipe.id}` && request.method === "GET") {
      response.end(JSON.stringify(submittedRecipe));
      return;
    }

    if (url.pathname === "/api/v1/products" && request.method === "GET") {
      response.end(JSON.stringify({ items: [editableRecipe.components[0].product] }));
      return;
    }

    if (
      url.pathname === `/api/v1/products/${editableRecipe.components[0].product.id}` &&
      request.method === "PUT"
    ) {
      editableRecipe.components[0].product = {
        ...editableRecipe.components[0].product,
        ...body,
      };
      response.end(JSON.stringify(editableRecipe.components[0].product));
      return;
    }

    if (
      url.pathname === `/api/v1/recipes/${submittedRecipe.id}/reject` &&
      request.method === "POST"
    ) {
      pending = false;
      submittedRecipe.lifecycle_status = "rejected";
      submittedRecipe.reviewed_by_user_id = 2;
      submittedRecipe.reviewed_by_display_name = "Проверяющий";
      submittedRecipe.reviewed_at = "2026-07-18T12:30:00+00:00";
      submittedRecipe.review_comment = body?.comment ?? null;
      submittedRecipe.can_publish = false;
      submittedRecipe.can_reject = false;
      response.end(JSON.stringify(submittedRecipe));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18102, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
