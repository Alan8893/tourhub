import { createServer } from "node:http";

export const auditExportRequests = [];

const event = {
  id: 21,
  actor_user_id: 1,
  actor_display_name: "Анна Администратор",
  actor_email: "admin@tourhub.local",
  actor_role: "administrator",
  action: "document_generated",
  entity_type: "project_document",
  entity_id: "42",
  before_data: null,
  after_data: {
    document_kind: "consolidated",
    format: "pdf",
  },
  context_data: { project_name: "Поход на Ладогу" },
  created_at: "2026-07-22T08:15:00Z",
};

function filteredEvents(url) {
  const action = url.searchParams.get("action");
  const entityType = url.searchParams.get("entity_type");
  return [event].filter(
    (item) =>
      (!action || item.action === action) &&
      (!entityType || item.entity_type === entityType),
  );
}

function csvCell(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function renderCsv(items) {
  const header = [
    "id",
    "created_at",
    "actor_display_name",
    "action",
    "entity_type",
    "entity_id",
    "after_json",
    "context_json",
  ];
  const rows = items.map((item) =>
    [
      item.id,
      item.created_at,
      item.actor_display_name,
      item.action,
      item.entity_type,
      item.entity_id,
      JSON.stringify(item.after_data),
      JSON.stringify(item.context_data),
    ]
      .map(csvCell)
      .join(","),
  );
  return `\ufeff${header.join(",")}\r\n${rows.join("\r\n")}\r\n`;
}

export function startAuditExportApi() {
  auditExportRequests.length = 0;
  const server = createServer((request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    auditExportRequests.push({
      method: request.method,
      path: url.pathname,
      query: Object.fromEntries(url.searchParams.entries()),
    });

    if (request.method === "GET" && url.pathname === "/api/v1/audit/events") {
      const items = filteredEvents(url);
      response.setHeader("content-type", "application/json");
      response.end(
        JSON.stringify({
          items,
          total: items.length,
          limit: Number(url.searchParams.get("limit") ?? 50),
          offset: 0,
        }),
      );
      return;
    }

    if (
      request.method === "GET" &&
      url.pathname === "/api/v1/audit/events/export.csv"
    ) {
      const items = filteredEvents(url);
      response.setHeader("content-type", "text/csv; charset=utf-8");
      response.setHeader(
        "content-disposition",
        'attachment; filename="tourhub-audit.csv"',
      );
      response.end(renderCsv(items));
      return;
    }

    response.statusCode = 404;
    response.setHeader("content-type", "application/json");
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18110, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
