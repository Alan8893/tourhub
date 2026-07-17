import { createServer } from "node:http";
import { domainToASCII } from "node:url";

export const requests = [];

function createSettings() {
  return {
    version: 1,
    expires_after_days: 7,
    default_role: "instructor",
    allowed_email_domains: [],
    allow_resend: true,
    active_invitation_limit: 100,
    administrators_only: true,
    require_email_confirmation: true,
    updated_at: "2026-07-17T18:40:00",
  };
}

function normalizeDomains(values) {
  return [...new Set(values.map((value) => domainToASCII(value.trim().toLowerCase().replace(/\.$/, ""))))]
    .filter(Boolean)
    .sort();
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startInvitationSettingsApi() {
  let settings = createSettings();
  let history = [];
  requests.length = 0;

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "PUT" ? await readBody(request) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/settings/invitations") {
      if (request.method === "PUT") {
        if (body.expected_version !== settings.version) {
          response.statusCode = 409;
          response.end(JSON.stringify({ error: "stale settings version" }));
          return;
        }
        if (!body.administrators_only) {
          response.statusCode = 422;
          response.end(JSON.stringify({ error: "Только администраторы могут управлять приглашениями." }));
          return;
        }
        const next = {
          ...body,
          allowed_email_domains: normalizeDomains(body.allowed_email_domains),
          version: settings.version + 1,
          updated_at: "2026-07-17T18:50:00",
        };
        delete next.expected_version;
        settings = next;
        history = [
          {
            id: 1,
            actor_label: "Локальный администратор",
            action: "updated",
            changed_fields: [
              "expires_after_days",
              "default_role",
              "allowed_email_domains",
              "allow_resend",
              "active_invitation_limit",
              "require_email_confirmation",
            ],
            settings_version: settings.version,
            created_at: "2026-07-17T18:50:00",
          },
        ];
      }
      response.statusCode = 200;
      response.end(JSON.stringify(settings));
      return;
    }

    if (url.pathname === "/api/v1/settings/invitations/history") {
      response.statusCode = 200;
      response.end(JSON.stringify(history));
      return;
    }

    if (url.pathname === "/api/v1/invitations" && request.method === "GET") {
      response.statusCode = 200;
      response.end(JSON.stringify([]));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18087, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
