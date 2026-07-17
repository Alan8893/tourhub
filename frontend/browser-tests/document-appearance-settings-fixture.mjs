import { createServer } from "node:http";

export const requests = [];

const IMAGE_DATA_URL =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl2n1cAAAAASUVORK5CYII=";

function createDocumentSettings() {
  return {
    version: 1,
    primary_color: "#1B5E20",
    accent_color: "#F9A825",
    heading_color: "#1B5E20",
    table_header_background: "#E8F2E8",
    table_header_text: "#162018",
    table_border_color: "#405047",
    title_background_color: "#F4F7F4",
    logo_source: "main_logo",
    show_contacts: true,
    footer_text: null,
    use_document_image_as_title_background: false,
    table_density: "comfortable",
    updated_at: "2026-07-17T12:00:00",
  };
}

function createClubSettings() {
  return {
    version: 2,
    club_name: "Турклуб Север",
    short_name: "Север",
    legal_name: null,
    description: null,
    address: "Москва, ул. Туристическая, 1",
    phone: "+7 900 000-00-00",
    email: "club@example.test",
    website: "https://example.test",
    timezone: "Europe/Moscow",
    city: "Москва",
    region: "Московская область",
    social_links: [],
    images: {
      main_logo_data_url: IMAGE_DATA_URL,
      light_logo_data_url: null,
      dark_logo_data_url: null,
      square_icon_data_url: null,
      favicon_data_url: null,
      login_background_data_url: null,
      document_image_data_url: IMAGE_DATA_URL,
    },
    updated_at: "2026-07-17T12:00:00",
  };
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startDocumentAppearanceApi() {
  let settings = createDocumentSettings();
  let history = [];
  requests.length = 0;

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "PUT" ? await readBody(request) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/settings/documents") {
      if (request.method === "PUT") {
        if (body.expected_version !== settings.version) {
          response.statusCode = 409;
          response.end(JSON.stringify({ error: "stale settings version" }));
          return;
        }
        settings = {
          ...body,
          version: settings.version + 1,
          updated_at: "2026-07-17T12:10:00",
        };
        delete settings.expected_version;
        history = [
          {
            id: 1,
            actor_label: "Локальный администратор",
            action: "updated",
            changed_fields: [
              "primary_color",
              "footer_text",
              "table_density",
              "use_document_image_as_title_background",
            ],
            settings_version: settings.version,
            created_at: "2026-07-17T12:10:00",
          },
        ];
      }
      response.statusCode = 200;
      response.end(JSON.stringify(settings));
      return;
    }

    if (url.pathname === "/api/v1/settings/documents/history") {
      response.statusCode = 200;
      response.end(JSON.stringify(history));
      return;
    }

    if (url.pathname === "/api/v1/settings/club") {
      response.statusCode = 200;
      response.end(JSON.stringify(createClubSettings()));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18085, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
