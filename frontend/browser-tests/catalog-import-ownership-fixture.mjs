import { createServer } from "node:http";

export const catalogImportOwnershipRequests = [];

const previewToken = "p".repeat(64);

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

function importResult(body, isPreview) {
  return {
    kind: body.kind,
    valid: true,
    row_count: 1,
    create_count: 1,
    skip_count: 0,
    component_count: 1,
    note_count: 1,
    ownership_scope: body.ownership_scope ?? null,
    preview_token: isPreview ? previewToken : body.preview_token ?? null,
    errors: [],
  };
}

export function startCatalogImportOwnershipApi() {
  catalogImportOwnershipRequests.length = 0;
  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    if (
      url.pathname === "/api/v1/catalog-import/preview" &&
      request.method === "POST"
    ) {
      const body = await readJson(request);
      catalogImportOwnershipRequests.push({
        method: request.method,
        path: url.pathname,
        body,
      });
      sendJson(response, importResult(body, true));
      return;
    }
    if (
      url.pathname === "/api/v1/catalog-import/apply" &&
      request.method === "POST"
    ) {
      const body = await readJson(request);
      catalogImportOwnershipRequests.push({
        method: request.method,
        path: url.pathname,
        body,
      });
      if (body.preview_token !== previewToken) {
        sendJson(response, { error: "preview token mismatch" }, 409);
        return;
      }
      sendJson(response, importResult(body, false));
      return;
    }
    sendJson(response, { error: "not found" }, 404);
  });

  return {
    previewToken,
    listen: () =>
      new Promise((resolve) => server.listen(18118, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
