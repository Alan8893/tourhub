import { createServer } from "node:http";

export const requests = [];

function createSettings() {
  return {
    version: 1,
    smtp_host: "localhost",
    smtp_port: 587,
    security_mode: "starttls",
    smtp_username: null,
    sender_email: "tourhub@localhost",
    sender_name: "TourHub",
    reply_to_email: null,
    test_recipient_email: null,
    timeout_seconds: 30,
    retry_count: 3,
    updated_at: "2026-07-17T20:00:00",
    secret_configured: true,
    secret_source: "environment",
    secret_environment_variable: "TOURHUB_SMTP_SECRET",
    delivery_available: false,
    test_delivery_available: false,
  };
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startMailSettingsApi() {
  let settings = createSettings();
  let history = [];
  requests.length = 0;

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "PUT" ? await readBody(request) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/settings/mail") {
      if (request.method === "PUT") {
        if (body.expected_version !== settings.version) {
          response.statusCode = 409;
          response.end(JSON.stringify({ error: "stale settings version" }));
          return;
        }
        const next = {
          ...body,
          smtp_host: body.smtp_host.trim().toLowerCase().replace(/\.$/, ""),
          smtp_username: body.smtp_username?.trim() || null,
          sender_email: body.sender_email.replace(/@(.+)$/, (_, domain) => `@${domain.toLowerCase()}`),
          sender_name: body.sender_name.trim(),
          reply_to_email: body.reply_to_email?.replace(
            /@(.+)$/,
            (_, domain) => `@${domain.toLowerCase()}`,
          ) || null,
          test_recipient_email: body.test_recipient_email?.replace(
            /@(.+)$/,
            (_, domain) => `@${domain.toLowerCase()}`,
          ) || null,
          version: settings.version + 1,
          updated_at: "2026-07-17T20:10:00",
          secret_configured: true,
          secret_source: "environment",
          secret_environment_variable: "TOURHUB_SMTP_SECRET",
          delivery_available: false,
          test_delivery_available: false,
        };
        delete next.expected_version;
        settings = next;
        history = [
          {
            id: 1,
            actor_label: "Локальный администратор",
            action: "updated",
            changed_fields: [
              "smtp_host",
              "smtp_port",
              "security_mode",
              "smtp_username",
              "sender_email",
              "sender_name",
              "reply_to_email",
              "test_recipient_email",
              "timeout_seconds",
              "retry_count",
            ],
            settings_version: settings.version,
            created_at: "2026-07-17T20:10:00",
          },
        ];
      }
      response.statusCode = 200;
      response.end(JSON.stringify(settings));
      return;
    }

    if (url.pathname === "/api/v1/settings/mail/history") {
      response.statusCode = 200;
      response.end(JSON.stringify(history));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18088, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
