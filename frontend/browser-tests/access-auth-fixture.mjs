import { createServer } from "node:http";

export const requests = [];

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  if (chunks.length === 0) return undefined;
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startAccessAuthApi() {
  let administrator = null;
  let member = null;
  let invitation = null;
  let invitationConsumed = false;
  requests.length = 0;

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "POST" ? await readBody(request).catch(() => undefined) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/auth/bootstrap-status") {
      response.end(JSON.stringify({ bootstrap_required: administrator === null }));
      return;
    }

    if (url.pathname === "/api/v1/auth/me") {
      const cookie = request.headers.cookie ?? "";
      if (cookie.includes("tourhub_session=admin-session") && administrator) {
        response.end(JSON.stringify({ user: administrator }));
        return;
      }
      if (cookie.includes("tourhub_session=member-session") && member) {
        response.end(JSON.stringify({ user: member }));
        return;
      }
      response.statusCode = 401;
      response.end(JSON.stringify({ error: "Требуется вход в TourHub." }));
      return;
    }

    if (url.pathname === "/api/v1/auth/bootstrap" && request.method === "POST") {
      if (administrator !== null) {
        response.statusCode = 409;
        response.end(JSON.stringify({ error: "Первый администратор уже создан." }));
        return;
      }
      administrator = {
        id: 1,
        email: String(body.email).trim().toLowerCase(),
        display_name: String(body.display_name).trim(),
        role: "administrator",
        is_active: true,
        created_at: "2026-07-18T00:00:00",
      };
      response.statusCode = 201;
      response.setHeader(
        "set-cookie",
        "tourhub_session=admin-session; HttpOnly; Path=/; SameSite=Lax",
      );
      response.end(JSON.stringify({ user: administrator }));
      return;
    }

    if (url.pathname === "/api/v1/auth/login" && request.method === "POST") {
      if (
        administrator === null ||
        String(body.email).trim().toLowerCase() !== administrator.email ||
        body.password !== "correct-horse-battery-staple"
      ) {
        response.statusCode = 401;
        response.end(JSON.stringify({ error: "Неверный email или пароль." }));
        return;
      }
      response.setHeader(
        "set-cookie",
        "tourhub_session=admin-session; HttpOnly; Path=/; SameSite=Lax",
      );
      response.end(JSON.stringify({ user: administrator }));
      return;
    }

    if (url.pathname === "/api/v1/auth/logout" && request.method === "POST") {
      response.statusCode = 204;
      response.setHeader(
        "set-cookie",
        "tourhub_session=; HttpOnly; Max-Age=0; Path=/; SameSite=Lax",
      );
      response.end();
      return;
    }

    if (url.pathname === "/api/v1/invitations" && request.method === "GET") {
      response.end(JSON.stringify(invitation ? [invitation] : []));
      return;
    }

    if (url.pathname === "/api/v1/invitations" && request.method === "POST") {
      invitation = {
        id: 1,
        email: String(body.email).trim().toLowerCase(),
        role: body.role ?? "instructor",
        status: "active",
        created_at: "2026-07-18T00:00:00",
        expires_at: "2026-07-25T00:00:00",
        consumed_at: null,
        revoked_at: null,
        superseded_at: null,
      };
      response.statusCode = 201;
      response.end(JSON.stringify({
        ...invitation,
        token: "access-link-test-code",
        acceptance_path: "/accept-invitation?token=access-link-test-code",
      }));
      return;
    }

    if (url.pathname === "/api/v1/invitations/inspect" && request.method === "POST") {
      if (body.token !== "access-link-test-code" || invitationConsumed || !invitation) {
        response.statusCode = 410;
        response.end(JSON.stringify({ error: "Приглашение уже использовано." }));
        return;
      }
      response.end(JSON.stringify({
        email: invitation.email,
        role: invitation.role,
        expires_at: invitation.expires_at,
      }));
      return;
    }

    if (url.pathname === "/api/v1/invitations/accept" && request.method === "POST") {
      if (body.token !== "access-link-test-code" || invitationConsumed || !invitation) {
        response.statusCode = 410;
        response.end(JSON.stringify({ error: "Приглашение уже использовано." }));
        return;
      }
      invitationConsumed = true;
      invitation.status = "consumed";
      invitation.consumed_at = "2026-07-18T00:05:00";
      member = {
        id: 2,
        email: invitation.email,
        display_name: String(body.display_name).trim(),
        role: invitation.role,
        is_active: true,
        created_at: "2026-07-18T00:05:00",
      };
      response.setHeader(
        "set-cookie",
        "tourhub_session=member-session; HttpOnly; Path=/; SameSite=Lax",
      );
      response.end(JSON.stringify({ user: member }));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18089, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
