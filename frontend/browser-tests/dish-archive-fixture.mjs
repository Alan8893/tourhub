import { createServer } from "node:http";

export const dishArchiveRequests = [];

function sendJson(response, payload, statusCode = 200) {
  response.statusCode = statusCode;
  response.setHeader("content-type", "application/json; charset=utf-8");
  response.end(JSON.stringify(payload));
}

function activeDish(id, name, recipeName) {
  const recipe = {
    id: `${id}-recipe`,
    name: recipeName,
    is_archived: false,
    scope: "club",
    owner_display_name: null,
    is_default: true,
  };
  return {
    id,
    name,
    recipe,
    recipes: [recipe],
    meal_roles: [],
  };
}

export function startDishArchiveApi() {
  let active = [
    activeDish("buckwheat-dish", "Гречневая каша", "Каша базовая"),
    activeDish("soup-dish", "Овощной суп", "Суп базовый"),
  ];
  let archived = [
    {
      id: "policy-wine-dish",
      name: "Глинтвейн",
      recipe_name: "Глинтвейн клубный",
      is_archived: true,
      archived_by_alcohol_policy: true,
    },
  ];
  dishArchiveRequests.length = 0;

  const server = createServer((request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    dishArchiveRequests.push({ method: request.method, path: url.pathname });

    if (url.pathname === "/api/v1/dishes" && request.method === "GET") {
      sendJson(response, { items: active });
      return;
    }
    if (url.pathname === "/api/v1/dishes/archive" && request.method === "GET") {
      sendJson(response, { items: archived });
      return;
    }

    const archiveMatch = url.pathname.match(/^\/api\/v1\/dishes\/([^/]+)\/archive$/);
    if (archiveMatch && request.method === "POST") {
      const dishId = decodeURIComponent(archiveMatch[1]);
      const dish = active.find((item) => item.id === dishId);
      if (!dish) {
        sendJson(response, { error: "Dish not found" }, 404);
        return;
      }
      active = active.filter((item) => item.id !== dishId);
      const archivedDish = {
        id: dish.id,
        name: dish.name,
        recipe_name: dish.recipe.name,
        is_archived: true,
        archived_by_alcohol_policy: false,
      };
      archived = [...archived, archivedDish];
      sendJson(response, archivedDish);
      return;
    }

    const restoreMatch = url.pathname.match(/^\/api\/v1\/dishes\/([^/]+)\/restore$/);
    if (restoreMatch && request.method === "POST") {
      const dishId = decodeURIComponent(restoreMatch[1]);
      const dish = archived.find((item) => item.id === dishId);
      if (!dish) {
        sendJson(response, { error: "Dish not found" }, 404);
        return;
      }
      if (dish.archived_by_alcohol_policy) {
        sendJson(
          response,
          {
            error: "Dish cannot be restored because it is blocked by the central alcohol policy",
          },
          409,
        );
        return;
      }
      archived = archived.filter((item) => item.id !== dishId);
      const restoredDish = activeDish(dish.id, dish.name, dish.recipe_name);
      active = [...active, restoredDish].sort((left, right) =>
        left.name.localeCompare(right.name, "ru"),
      );
      sendJson(response, {
        ...dish,
        is_archived: false,
      });
      return;
    }

    sendJson(response, { error: "not found" }, 404);
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18117, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
