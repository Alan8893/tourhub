# TourHub Current Roadmap

Status date: 2026-07-17

## Product goal

Deliver a stable local MVP for one tourist club without changing the approved architecture.

```text
Project
  → Menu
  → Recipes and dishes
  → Shopping and packaging
  → Equipment
  → Branded Russian PDF and Excel
  → Guided release acceptance
```

## DONE

### Infrastructure

- Docker Compose, PostgreSQL, Redis, and Alembic one-head validation;
- backend Ruff, strict mypy, pytest, frontend tests/build/browser acceptance;
- PostgreSQL backup/restore CI;
- LAN-safe routing and responsive navigation.

### Preparation workflow through merged PR #76

- project creation, workspace, participants, duration, and meal boundaries;
- catalogues, CSV import, role-aware menu generation, and manual editing;
- persisted shopping, packaging, surplus, and purchasing contact;
- persisted equipment requirements, project overrides, and transactional recalculation;
- Russian purchase and equipment PDF/Excel plus five-file ZIP package;
- focused document quality and real-browser desktop/mobile acceptance.

PR #76 merged as `51ea7785f12e8d1d30b2768284b6fddbb0117872`.

## IN PROGRESS

### PR #77 — persistent club branding

- persist singleton club name and optional logo through Alembic `h10007`;
- validate PNG/JPEG MIME, decoded image content, size, and dimensions;
- provide Russian settings UI with preview and removal;
- apply one consistent branding snapshot to every generated project document;
- verify settings API, PDF/XLSX branding, browser PUT body, screenshot, and 360 px layout.

PR #77 exact head `317d3b013e0a24c224c8b291e06f49bef349305d` passed Quality #416 and Document Quality #49 and is Ready.

### Stacked PR #78 — guided release acceptance

- expose persisted preparation readiness without mutation;
- restore menu, purchase, checklist, equipment, and document readiness after reload;
- require equipment before completion;
- treat missing derived documents as unprepared, not server errors;
- verify create → menu → prepare → reload → branded ZIP in the full application;
- capture desktop flow, exact API requests, 360 px no-overflow, screenshot evidence, and focused failure diagnostics.

Functional head `b247b2d7c2dd38c9874e92c524a66f25b293e3bf` passed Quality #421, Document Quality #54, and Guided Release Acceptance #5 before documentation synchronization.

## NEXT

- merge PR #77 and retarget/rebase PR #78 to `main`;
- add installation and update documentation;
- add Docker image/build and PostgreSQL migration smoke gates;
- complete the final release workflow.

## LATER

- invitation-only registration and roles;
- recipe ownership, variants, publication, and moderation;
- audit log;
- participant profiles, routes, logistics, and load distribution;
- warehouse balances and price aggregation.

Multi-tenant support and microservices remain prohibited.
