import { createServer } from "node:http";

export const requests = [];

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startAccessAuthApi() {
  let user = null;
  let activeSession = false;
  requests.length = 0;

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "POST" ? await readBody(request).catch(() => undefined) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/auth/bootstrap-status") {
      response.end(JSON.stringify({ bootstrap_required: user === null }));
      return;
    }

    if (url.pathname === "/api/v1/auth/me") {
      if (!activeSession || !request.headers.cookie?.includes("tourhub_session=test-session")) {
        response.statusCode = 401;
        response.end(JSON.stringify({ error: "Требуется вход в TourHub." }));
        return;
      }
      response.end(JSON.stringify({ user }));
      return;
    }

    if (url.pathname === "/api/v1/session-probe") {
      if (!activeSession || !request.headers.cookie?.includes("tourhub_session=test-session")) {
        response.statusCode = 401;
        response.end(JSON.stringify({ error: "Сессия завершена администратором." }));
        return;
      }
      response.end(JSON.stringify({ status: "active" }));
      return;
    }

    if (url.pathname === "/api/v1/auth/bootstrap" && request.method === "POST") {
      if (user !== null) {
        response.statusCode = 409;
        response.end(JSON.stringify({ error: "Первый администратор уже создан." }));
        return;
      }
      user = {
        id: 1,
        email: String(body.email).trim().toLowerCase(),
        display_name: String(body.display_name).trim(),
        role: "administrator",
        is_active: true,
        created_at: "2026-07-18T00:00:00",
      };
      activeSession = true;
      response.statusCode = 201;
      response.setHeader(
        "set-cookie",
        "tourhub_session=test-session; HttpOnly; Path=/; SameSite=Lax",
      );
      response.end(JSON.stringify({ user }));
      return;
    }

    if (url.pathname === "/api/v1/auth/login" && request.method === "POST") {
      if (
        user === null ||
        String(body.email).trim().toLowerCase() !== user.email ||
        body.password !== "correct-horse-battery-staple"
      ) {
        response.statusCode = 401;
        response.end(JSON.stringify({ error: "Неверный email или пароль." }));
        return;
      }
      activeSession = true;
      response.setHeader(
        "set-cookie",
        "tourhub_session=test-session; HttpOnly; Path=/; SameSite=Lax",
      );
      response.end(JSON.stringify({ user }));
      return;
    }

    if (url.pathname === "/api/v1/auth/logout" && request.method === "POST") {
      activeSession = false;
      response.statusCode = 204;
      response.setHeader(
        "set-cookie",
        "tourhub_session=; HttpOnly; Max-Age=0; Path=/; SameSite=Lax",
      );
      response.end();
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18089, "127.0.0.1", resolve)),
    invalidateSession: () => {
      activeSession = false;
    },
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
