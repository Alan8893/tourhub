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

    if (url.pathname === "/api/v1/account/password" && request.method === "POST") {
      if (body.current_password !== "current-account-password") {
        response.statusCode = 400;
        response.setHeader("content-type", "application/json");
        response.end(JSON.stringify({ detail: "Текущий пароль указан неверно." }));
        return;
      }
      profile = { ...profile, version: profile.version + 1 };
      response.setHeader("content-type", "application/json");
      response.end(JSON.stringify(profile));
      return;
    }

    if (url.pathname === "/api/v1/account/contacts" && request.method === "GET") {
      response.setHeader("content-type", "application/json");
      response.end(
        JSON.stringify([
          {
            id: profile.id,
            email: profile.email,
            display_name: profile.display_name,
            phone: profile.phone,
            telegram_url: profile.telegram_url,
            max_url: profile.max_url,
            vk_url: profile.vk_url,
            role: profile.role,
            is_current: true,
          },
          {
            id: 2,
            email: "boris@club.example",
            display_name: "Борис Инструктор",
            phone: "+491234567890",
            telegram_url: "https://t.me/boris_guide",
            max_url: "https://max.ru/boris-guide",
            vk_url: "https://vk.com/id12345",
            role: "verified_instructor",
            is_current: false,
          },
        ]),
      );
      return;
    }

    if (url.pathname === "/api/v1/account/contacts/2/vcard" && request.method === "GET") {
      response.setHeader("content-type", "text/vcard; charset=utf-8");
      response.setHeader(
        "content-disposition",
        'attachment; filename="tourhub-contact-2.vcf"',
      );
      response.end(
        "BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Борис Инструктор\r\nTEL;TYPE=CELL:+491234567890\r\nEND:VCARD\r\n",
      );
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
