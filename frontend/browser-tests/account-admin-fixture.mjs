import { createServer } from "node:http";

export const requests = [];

const users = [
  {
    id: 1,
    email: "admin@tourhub.local",
    display_name: "Локальный администратор",
    role: "administrator",
    is_active: true,
    version: 1,
    created_at: "2026-07-18T00:00:00",
    updated_at: "2026-07-18T00:00:00",
    last_login_at: "2026-07-18T00:10:00",
    is_current: true,
  },
  {
    id: 2,
    email: "member@example.org",
    display_name: "Новый инструктор",
    role: "instructor",
    is_active: true,
    version: 1,
    created_at: "2026-07-18T00:05:00",
    updated_at: "2026-07-18T00:05:00",
    last_login_at: null,
    is_current: false,
  },
];

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startAccountAdminApi() {
  requests.length = 0;
  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "PATCH" ? await readBody(request) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/users" && request.method === "GET") {
      response.end(JSON.stringify(users));
      return;
    }

    if (url.pathname === "/api/v1/users/2" && request.method === "PATCH") {
      if (body.expected_version !== users[1].version) {
        response.statusCode = 409;
        response.end(JSON.stringify({ error: "Данные пользователя изменились." }));
        return;
      }
      users[1] = {
        ...users[1],
        role: body.role,
        is_active: body.is_active,
        version: users[1].version + 1,
        updated_at: "2026-07-18T00:20:00",
      };
      response.end(JSON.stringify(users[1]));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18092, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
