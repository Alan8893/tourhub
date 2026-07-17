# TH-0077 — System Settings Module Visibility

Status: DONE

Last updated: 2026-07-17

## Goal

Add a typed `Модули` settings section that controls navigation visibility without changing route or API availability, while the backend enforces required modules and dependency locks.

## Delivered

- singleton typed `ModuleSettings` persistence;
- additive Alembic `h10011` with one head;
- required `Проекты` and `Каталог` visibility;
- configurable `Импорт`, `Закупка`, `Оборудование`, and `Документы` visibility;
- backend and database dependency locks for visible documents;
- versioned row-locked updates, HTTP 409 conflicts, and safe focused history;
- immediate desktop/mobile sidebar and project-workspace visibility updates;
- direct URL and API availability preserved;
- full backend, frontend, browser, PostgreSQL, Docker, document, and operator validation.

Merged in PR #87 as `717d6f22d58e86a952edad501f05d3c67d8c0bf4`.
