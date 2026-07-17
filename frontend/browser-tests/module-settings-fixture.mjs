import { createServer } from "node:http";

export const requests = [];

function definitions(settings) {
  return [
    {
      key: "projects",
      label: "Проекты",
      description: "Каталог походов и рабочее пространство подготовки.",
      visible: settings.projects_visible,
      required: true,
      dependencies: [],
      locked: true,
      lock_reason: "Модуль «Проекты» обязателен для текущего MVP.",
    },
    {
      key: "catalogue",
      label: "Каталог",
      description: "Блюда и рецепты, используемые меню и расчётами.",
      visible: settings.catalogue_visible,
      required: true,
      dependencies: [],
      locked: true,
      lock_reason: "Модуль «Каталог» обязателен для текущего MVP.",
    },
    {
      key: "catalog_import",
      label: "Импорт",
      description: "Загрузка и проверка каталогов через CSV.",
      visible: settings.catalog_import_visible,
      required: false,
      dependencies: ["catalogue"],
      locked: false,
      lock_reason: null,
    },
    {
      key: "shopping",
      label: "Закупка",
      description: "Раскладка, упаковки, список закупки и чек-лист.",
      visible: settings.shopping_visible,
      required: false,
      dependencies: [],
      locked: settings.documents_visible,
      lock_reason: settings.documents_visible
        ? "Нельзя скрыть, пока виден модуль «Документы»."
        : null,
    },
    {
      key: "equipment",
      label: "Оборудование",
      description: "Расчёт и ручная корректировка снаряжения проекта.",
      visible: settings.equipment_visible,
      required: false,
      dependencies: [],
      locked: settings.documents_visible,
      lock_reason: settings.documents_visible
        ? "Нельзя скрыть, пока виден модуль «Документы»."
        : null,
    },
    {
      key: "documents",
      label: "Документы",
      description: "PDF, Excel, печатная версия и ZIP проекта.",
      visible: settings.documents_visible,
      required: false,
      dependencies: ["shopping", "equipment"],
      locked: false,
      lock_reason: null,
    },
  ];
}

function createSettings() {
  const settings = {
    version: 1,
    projects_visible: true,
    catalogue_visible: true,
    catalog_import_visible: true,
    shopping_visible: true,
    equipment_visible: true,
    documents_visible: true,
    updated_at: "2026-07-17T18:00:00",
  };
  return { ...settings, modules: definitions(settings) };
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

export function startModuleSettingsApi() {
  let settings = createSettings();
  let history = [];
  requests.length = 0;

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "PUT" ? await readBody(request) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/settings/modules") {
      if (request.method === "PUT") {
        if (body.expected_version !== settings.version) {
          response.statusCode = 409;
          response.end(JSON.stringify({ error: "stale settings version" }));
          return;
        }
        if (!body.projects_visible || !body.catalogue_visible) {
          response.statusCode = 400;
          response.end(JSON.stringify({ error: "Обязательный модуль нельзя скрыть." }));
          return;
        }
        if (body.documents_visible && (!body.shopping_visible || !body.equipment_visible)) {
          response.statusCode = 400;
          response.end(JSON.stringify({ error: "Документы требуют закупку и оборудование." }));
          return;
        }
        const next = {
          ...body,
          version: settings.version + 1,
          updated_at: "2026-07-17T18:10:00",
        };
        delete next.expected_version;
        settings = { ...next, modules: definitions(next) };
        history = [
          {
            id: 1,
            actor_label: "Локальный администратор",
            action: "updated",
            changed_fields: [
              "catalog_import_visible",
              "shopping_visible",
              "equipment_visible",
              "documents_visible",
            ],
            settings_version: settings.version,
            created_at: "2026-07-17T18:10:00",
          },
        ];
      }
      response.statusCode = 200;
      response.end(JSON.stringify(settings));
      return;
    }

    if (url.pathname === "/api/v1/settings/modules/history") {
      response.statusCode = 200;
      response.end(JSON.stringify(history));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: "not found" }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18086, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}
