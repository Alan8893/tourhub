import { createServer } from "node:http";

export const requests = [];

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  if (chunks.length === 0) return undefined;
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startInvitationLifecycleApi() {
  const records = [];
  let memberSession = false;
  let consumed = false;
  let nextId = 1;
  requests.length = 0;

  const member = {
    id: 2,
    email: "member@club.example",
    display_name: "Новый инструктор",
    role: "instructor",
    is_active: true,
    created_at: "2026-07-18T00:00:00",
  };

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "POST" ? await readBody(request).catch(() => undefined) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/auth/bootstrap-status") {
      response.end(JSON.stringify({ bootstrap_required: false }));
      return;
    }
    if (url.pathname === "/api/v1/auth/me") {
      if (!memberSession || !request.headers.cookie?.includes("tourhub_session=member-session")) {
        response.statusCode = 401;
        response.end(JSON.stringify({ error: "Требуется вход в TourHub." }));
        return;
      }
      response.end(JSON.stringify({ user: member }));
      return;
    }
    if (url.pathname === "/api/v1/invitations" && request.method === "GET") {
      response.end(JSON.stringify([...records].reverse()));
      return;
    }
    if (url.pathname === "/api/v1/invitations" && request.method === "POST") {
      const record = {
        id: nextId++,
        email: String(body.email).trim().toLowerCase(),
        role: body.role ?? "instructor",
        status: "active",
        created_at: "2026-07-18T00:00:00",
        expires_at: "2026-07-25T00:00:00",
        consumed_at: null,
        revoked_at: null,
        superseded_at: null,
      };
      records.push(record);
      response.statusCode = 201;
      response.end(JSON.stringify({
        ...record,
        token: "invitation-lifecycle-test-code",
        acceptance_path: "/accept-invitation?token=invitation-lifecycle-test-code",
      }));
      return;
    }
    if (url.pathname === "/api/v1/invitations/inspect" && request.method === "POST") {
      if (body.token !== "invitation-lifecycle-test-code" || consumed) {
        response.statusCode = 410;
        response.end(JSON.stringify({ error: "Приглашение уже использовано." }));
        return;
      }
      response.end(JSON.stringify({
        email: member.email,
        role: member.role,
        expires_at: "2026-07-25T00:00:00",
      }));
      return;
    }
    if (url.pathname === "/api/v1/invitations/accept" && request.method === "POST") {
      if (body.token !== "invitation-lifecycle-test-code" || consumed) {
        response.statusCode = 410;
        response.end(JSON.stringify({ error: "Приглашение уже использовано." }));
        return;
      }
      consumed = true;
      memberSession = true;
      records[0].status = "consumed";
      records[0].consumed_at = "2026-07-18T00:05:00";
      response.setHeader(
        "set-cookie",
        "tourhub_session=member-session; HttpOnly; Path=/; SameSite=Lax",
      );
      response.end(JSON.stringify({ user: { ...member, display_name: String(body.display_name).trim() } }));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18090, "127.0.0.1", resolve)),
    close: () => new Promise((resolve) => {
      server.closeAllConnections();
      server.close(resolve);
    }),
  };
}
