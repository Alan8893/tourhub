import { createServer } from "node:http";

export const productArchiveRequests = [];

function sendJson(response, payload, statusCode = 200) {
  response.statusCode = statusCode;
  response.setHeader("content-type", "application/json; charset=utf-8");
  response.end(JSON.stringify(payload));
}

export function startProductArchiveApi() {
  let active = [
    {
      id: "buckwheat",
      name: "Гречка",
      category: "Крупы",
      unit: "gram",
      package_size: 800,
      is_archived: false,
      archived_by_alcohol_policy: false,
    },
    {
      id: "rice",
      name: "Рис",
      category: "Крупы",
      unit: "gram",
      package_size: 900,
      is_archived: false,
      archived_by_alcohol_policy: false,
    },
  ];
  let archived = [
    {
      id: "policy-wine",
      name: "Вино",
      category: "Алкоголь",
      unit: "milliliter",
      package_size: 750,
      is_archived: true,
      archived_by_alcohol_policy: true,
    },
  ];
  productArchiveRequests.length = 0;

  const server = createServer((request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    productArchiveRequests.push({ method: request.method, path: url.pathname });

    if (url.pathname === "/api/v1/products" && request.method === "GET") {
      sendJson(response, { items: active });
      return;
    }
    if (url.pathname === "/api/v1/products/archive" && request.method === "GET") {
      sendJson(response, { items: archived });
      return;
    }

    const archiveMatch = url.pathname.match(/^\/api\/v1\/products\/([^/]+)\/archive$/);
    if (archiveMatch && request.method === "POST") {
      const productId = decodeURIComponent(archiveMatch[1]);
      const product = active.find((item) => item.id === productId);
      if (!product) {
        sendJson(response, { error: "Product not found" }, 404);
        return;
      }
      active = active.filter((item) => item.id !== productId);
      const archivedProduct = { ...product, is_archived: true };
      archived = [...archived, archivedProduct];
      sendJson(response, archivedProduct);
      return;
    }

    const restoreMatch = url.pathname.match(/^\/api\/v1\/products\/([^/]+)\/restore$/);
    if (restoreMatch && request.method === "POST") {
      const productId = decodeURIComponent(restoreMatch[1]);
      const product = archived.find((item) => item.id === productId);
      if (!product) {
        sendJson(response, { error: "Product not found" }, 404);
        return;
      }
      if (product.archived_by_alcohol_policy) {
        sendJson(
          response,
          {
            error:
              "Product cannot be restored because it is blocked by the central alcohol policy",
          },
          409,
        );
        return;
      }
      archived = archived.filter((item) => item.id !== productId);
      const restoredProduct = { ...product, is_archived: false };
      active = [...active, restoredProduct].sort((left, right) =>
        left.name.localeCompare(right.name, "ru"),
      );
      sendJson(response, restoredProduct);
      return;
    }

    sendJson(response, { error: "not found" }, 404);
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18116, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
