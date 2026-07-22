import { createServer } from "node:http";

export const accountRequests = [];

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  if (chunks.length === 0) return undefined;
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startAccountProfileApi() {
  let profile = {
    id: 1,
    email: "irina@club.example",
    display_name: "Ирина Инструктор",
    phone: null,
    telegram_url: null,
    max_url: null,
    vk_url: null,
    role: "instructor",
    is_active: true,
    version: 1,
    created_at: "2026-07-01T10:00:00Z",
    updated_at: "2026-07-01T10:00:00Z",
  };
  let sessions = [
    {
      id: 101,
      created_at: "2026-07-22T08:00:00Z",
      last_seen_at: "2026-07-22T10:00:00Z",
      expires_at: "2026-08-21T08:00:00Z",
      is_current: true,
    },
    {
      id: 202,
      created_at: "2026-07-20T07:30:00Z",
      last_seen_at: "2026-07-21T18:45:00Z",
      expires_at: "2026-08-19T07:30:00Z",
      is_current: false,
    },
  ];
  let loggedOut = false;
  accountRequests.length = 0;

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = ["POST", "PATCH", "PUT"].includes(request.method ?? "")
      ? await readBody(request).catch(() => undefined)
      : undefined;
    accountRequests.push({ method: request.method, path: url.pathname, body });

    if (url.pathname === "/api/v1/account" && request.method === "GET") {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify(profile));
      return;
    }

    if (url.pathname === "/api/v1/account" && request.method === "PATCH") {
      profile = {
        ...profile,
        display_name: String(body.display_name).trim(),
        phone: body.phone ? "+79991234567" : null,
        telegram_url: body.telegram_url ? "https://t.me/irina_guide" : null,
        max_url: body.max_url ? "https://max.ru/irina-guide" : null,
        vk_url: body.vk_url ? "https://vk.com/irina-guide" : null,
        version: profile.version + 1,
        updated_at: "2026-07-21T12:00:00Z",
      };
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify(profile));
      return;
    }

    if (url.pathname === "/api/v1/account/sessions" && request.method === "GET") {
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify(sessions));
      return;
    }

    const sessionMatch = url.pathname.match(/^\/api\/v1\/account\/sessions\/(\d+)$/);
    if (sessionMatch && request.method === "DELETE") {
      const sessionId = Number(sessionMatch[1]);
      const target = sessions.find((session) => session.id === sessionId);
      if (!target || target.is_current) {
        response.statusCode = target ? 409 : 404;
        response.setHeader("content-type", "application/json");
        response.end(
          JSON.stringify({
            error: target
              ? "Текущую сессию можно завершить только обычным выходом."
              : "Активная сессия не найдена.",
          }),
        );
        return;
      }
      sessions = sessions.filter((session) => session.id !== sessionId);
      response.statusCode = 204;
      response.end();
      return;
    }

    if (url.pathname === "/api/v1/account/password" && request.method === "POST") {
      if (body.current_password !== "current-account-password") {
        response.statusCode = 400;
        response.setHeader("content-type", "application/json");
        response.end(JSON.stringify({ detail: "Текущий пароль указан неверно." }));
        return;
      }
      profile = { ...profile, version: profile.version + 1 };
      sessions = sessions.filter((session) => session.is_current);
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify(profile));
      return;
    }

    if (url.pathname === "/api/v1/auth/logout" && request.method === "POST") {
      loggedOut = true;
      response.statusCode = 204;
      response.end();
      return;
    }

    response.statusCode = 404;
    response.setHeader("content-type", "application/json");
    response.end(JSON.stringify({ error: "not found", loggedOut }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18098, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
