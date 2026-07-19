import { createServer } from "node:http";

export const requests = [];

const routes = new Map([
  ["/api/v1/projects/91/documents/consolidated/pdf", "application/pdf"],
  [
    "/api/v1/projects/91/documents/consolidated/excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  ],
  ["/api/v1/projects/91/documents/package", "application/zip"],
]);

export function startConsolidatedDocumentsApi() {
  requests.length = 0;
  const server = createServer((request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    requests.push({ method: request.method ?? "GET", path: url.pathname });
    const contentType = routes.get(url.pathname);
    if (request.method === "GET" && contentType) {
      response.statusCode = 200;
      response.setHeader("content-type", contentType);
      response.end(Buffer.from(`document:${url.pathname}`));
      return;
    }
    response.statusCode = 404;
    response.setHeader("content-type", "application/json");
    response.end(JSON.stringify({ detail: `Unhandled mock path: ${url.pathname}` }));
  });

  return {
    listen: () =>
      new Promise((resolve, reject) => {
        server.once("error", reject);
        server.listen(18094, "127.0.0.1", resolve);
      }),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
