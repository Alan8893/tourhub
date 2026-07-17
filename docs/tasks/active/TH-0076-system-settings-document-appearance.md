# TH-0076 — System Settings Document Appearance

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Add a typed `Документы` settings section that controls PDF, Excel, printable text, and ZIP branding through one immutable snapshot loaded once per generation request.

## Product decisions

- document appearance is independent from site appearance;
- all generated files in one ZIP must observe the exact same snapshot;
- organization colors and document controls are global for the installation;
- primary/accent/heading/table colors are configurable;
- the club can choose which approved club image is used as the document logo;
- the optional document image can be used as a title background/banner;
- club contacts can be shown or hidden;
- a custom Russian footer is optional;
- table density is comfortable or compact;
- changes apply to subsequent generations without an application restart;
- saving is section-specific, versioned, and recorded in safe focused history;
- document settings never contain secrets.

## Scope

### Backend

- add singleton `document_appearance_settings` persistence with version and timestamps;
- store validated document palette, logo source, title-background choice, contacts visibility, footer, and table density;
- reject stale writes with HTTP 409 and serialize concurrent writes with a PostgreSQL row lock;
- expose GET/PUT/history endpoints under `/api/v1/settings/documents`;
- append safe `documents` history records and retain the latest 200 settings-history rows;
- build one frozen document-branding snapshot from `ClubSettings` plus `DocumentAppearanceSettings`;
- load that snapshot once in `ProjectDocumentService` and reuse it for purchase/equipment PDF, XLSX, print, and ZIP generation;
- add one additive Alembic migration and keep one head.

### Frontend

- replace the planned `Документы` placeholder with a responsive editor;
- edit colors, table density, logo source, contacts visibility, custom footer, and title-background use;
- show an isolated document preview before saving;
- provide reset and cancel actions;
- show validation, saved state, version conflicts, and history in Russian.

### Document rendering

- PDF uses configured headings, table header/background/text/border colors, density, logo, contacts, footer, and optional title banner;
- Excel uses the same palette, density, metadata, header/footer, logo, contacts, and optional title banner placement;
- printable text includes the same club identity, optional contacts, and custom footer;
- ZIP uses one immutable snapshot for every contained document.

## Out of scope

- consolidated document contents beyond existing purchase/equipment exports;
- arbitrary templates, CSS, uploaded fonts, or rich-text footer markup;
- per-project document themes;
- module visibility, invitations, users, authentication, authorization, SMTP, or encrypted full-system archives.

## Acceptance criteria

- document settings persist and reload independently from club and site appearance settings;
- invalid colors or unreadable table-header contrast are rejected with a clear reason;
- stale writes return HTTP 409 and do not overwrite newer data;
- every approved logo source and fallback behaves predictably;
- one package generation reads club/document settings once and uses the same frozen snapshot for all files;
- existing document endpoints and filenames remain compatible;
- PDF, XLSX, print, and ZIP reflect saved settings on the next generation without restart;
- history contains changed field names only and no binary data;
- Alembic has one head;
- backend, frontend, browser, document, PostgreSQL, Docker, and full exact-head Quality gates pass.