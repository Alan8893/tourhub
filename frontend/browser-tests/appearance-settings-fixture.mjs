import { createServer } from "node:http";

export const requests = [];

const TOURHUB_LIGHT = {
  primary: "#1B5E20",
  secondary: "#2E7D32",
  accent: "#F9A825",
  background: "#F4F7F4",
  paper: "#FFFFFF",
  sidebar: "#E8F2E8",
  appbar: "#1B5E20",
  text_primary: "#162018",
  text_secondary: "#435348",
  divider: "#C8D2CA",
  success: "#2E7D32",
  warning: "#ED6C02",
  error: "#D32F2F",
};

const TOURHUB_DARK = {
  primary: "#81C784",
  secondary: "#A5D6A7",
  accent: "#FFD54F",
  background: "#101713",
  paper: "#18211B",
  sidebar: "#1E2A22",
  appbar: "#16351D",
  text_primary: "#F2F7F3",
  text_secondary: "#C1CDC4",
  divider: "#405047",
  success: "#81C784",
  warning: "#FFB74D",
  error: "#EF9A9A",
};

const OCEAN_LIGHT = {
  ...TOURHUB_LIGHT,
  primary: "#075985",
  secondary: "#0369A1",
  accent: "#0F766E",
  background: "#F1F7FA",
  sidebar: "#E1EFF5",
  appbar: "#075985",
  text_primary: "#10242E",
  text_secondary: "#405D6B",
};

const OCEAN_DARK = {
  ...TOURHUB_DARK,
  primary: "#7DD3FC",
  secondary: "#BAE6FD",
  accent: "#5EEAD4",
  background: "#0B151B",
  paper: "#13222B",
  sidebar: "#172A35",
  appbar: "#0C3A55",
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function createAppearance() {
  return {
    version: 1,
    preset_name: "tourhub",
    font_family: "system",
    density: "comfortable",
    border_radius: 10,
    button_style: "contained",
    card_style: "outlined",
    shadows_enabled: true,
    light: clone(TOURHUB_LIGHT),
    dark: clone(TOURHUB_DARK),
    updated_at: "2026-07-17T12:00:00",
  };
}

function preset(label, values) {
  const { version, updated_at, ...theme } = createAppearance();
  return { label, ...theme, ...values };
}

function presets() {
  return [
    preset("TourHub", {}),
    preset("Лес", {
      preset_name: "forest",
      font_family: "humanist",
      border_radius: 12,
    }),
    preset("Океан", {
      preset_name: "ocean",
      font_family: "modern",
      border_radius: 8,
      card_style: "elevated",
      light: clone(OCEAN_LIGHT),
      dark: clone(OCEAN_DARK),
    }),
    preset("Закат", {
      preset_name: "sunset",
      density: "compact",
      border_radius: 14,
    }),
  ];
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startAppearanceApi() {
  let appearance = createAppearance();
  let history = [];
  requests.length = 0;

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "PUT" ? await readBody(request) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/settings/appearance") {
      if (request.method === "PUT") {
        if (body.expected_version !== appearance.version) {
          response.statusCode = 409;
          response.end(JSON.stringify({ error: "stale settings version" }));
          return;
        }
        appearance = {
          ...body,
          version: appearance.version + 1,
          updated_at: "2026-07-17T12:10:00",
        };
        delete appearance.expected_version;
        history = [
          {
            id: 1,
            actor_label: "Локальный администратор",
            action: "updated",
            changed_fields: ["preset_name", "font_family", "light.primary"],
            settings_version: appearance.version,
            created_at: "2026-07-17T12:10:00",
          },
        ];
      }
      response.statusCode = 200;
      response.end(JSON.stringify(appearance));
      return;
    }

    if (url.pathname === "/api/v1/settings/appearance/presets") {
      response.statusCode = 200;
      response.end(JSON.stringify(presets()));
      return;
    }

    if (url.pathname === "/api/v1/settings/appearance/history") {
      response.statusCode = 200;
      response.end(JSON.stringify(history));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18084, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
