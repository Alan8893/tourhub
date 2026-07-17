# TH-0077 — System Settings Module Visibility

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Add a typed `Модули` settings section that controls navigation visibility without changing route or API availability, while the backend enforces required modules and dependency locks.

## Product decisions

- the first module slice affects navigation and project-workspace cards only;
- direct URLs and APIs remain available;
- `Проекты` and `Каталог` are required and cannot be hidden;
- `Импорт`, `Закупка`, `Оборудование`, and `Документы` are optional visibility modules;
- visible `Документы` require visible `Закупка` and `Оборудование`;
- dependency validation belongs to the backend and returns a Russian explanation;
- saving is section-specific, versioned, row-locked, and recorded in safe history;
- module settings contain no secrets and do not implement authorization.

## Scope

### Backend

- add singleton `module_settings` persistence with explicit boolean columns, version, and timestamps;
- expose typed GET/PUT/history endpoints under `/api/v1/settings/modules`;
- return module metadata including labels, descriptions, required state, dependencies, and lock reasons;
- reject attempts to hide required modules;
- reject states where visible documents lose shopping or equipment dependencies;
- use optimistic versioning, a PostgreSQL row lock, HTTP 409 conflicts, and safe focused history;
- add additive Alembic `h10011` and keep one head.

### Frontend

- replace the planned `Модули` placeholder with a responsive editor;
- show required and dependency-locked switches with Russian explanations;
- provide reset, cancel, save, conflict, version, and history states;
- apply saved visibility immediately to the desktop/mobile sidebar;
- hide optional project-workspace cards without removing their routes or APIs.

### Visibility map

- `projects` -> sidebar `Проекты`, required;
- `catalogue` -> sidebar `Блюда` and `Рецепты`, required;
- `catalog_import` -> sidebar `Импорт`;
- `shopping` -> project shopping and purchase cards;
- `equipment` -> project equipment card;
- `documents` -> project documents card and depends on shopping plus equipment;
- `Настройки` remains visible and is not configurable in this slice.

## Out of scope

- route guards, API disabling, permissions, roles, authentication, or authorization;
- runtime unloading of backend modules;
- invitation policy fields or a functional invitation list;
- SMTP or mail delivery;
- per-user module preferences;
- arbitrary module registration or generic key/value settings.

## Acceptance criteria

- settings persist and reload independently;
- required modules cannot be hidden;
- documents cannot remain visible when shopping or equipment is hidden;
- dependency failures return a clear Russian reason and do not partially save;
- saved visibility updates sidebar and project cards without restart;
- hidden routes remain directly accessible and APIs remain unchanged;
- stale writes return HTTP 409;
- history stores field names only;
- Alembic has one head `h10011`;
- backend, frontend, browser, PostgreSQL, Docker, document, operator, and exact-head Quality gates pass.