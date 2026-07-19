# TH-0095 — Project Workspace Navigation and Responsive Layout

Status: DONE

Completed: 2026-07-19

Pull request: #105

## Goal

Replace the Project page's very long landing layout with a compact routed workspace that is practical on desktop, tablet, and mobile screens while preserving all released v0.1.0 preparation behavior.

## User evidence

The approved implementation responds to real screenshots of a prepared Project at approximately 831 px viewport width:

- the permanent global sidebar consumed a large part of the available width;
- Menu, packing, purchase checklist, equipment, and documents were rendered in one very long page;
- the two-column Shopping/Checklist layout compressed checklist controls into unreadable narrow rows;
- finding a specific work area required extensive vertical scrolling.

The Product Owner approved the visual sketch with a compact Overview, section tabs, a hidden tablet/mobile sidebar, and dedicated Menu, Shopping, Equipment, and Documents views.

## Delivered scope

- Project workspace routes:
  - `/projects/:id` — Overview;
  - `/projects/:id/menu`;
  - `/projects/:id/shopping`;
  - `/projects/:id/equipment`;
  - `/projects/:id/documents`.
- Compact Overview with:
  - readiness progress;
  - direct actions for Menu, Shopping, and Equipment;
  - compact full-package document download;
  - existing generate/prepare next action.
- Project Recipe generation mode moved from the always-visible landing card into a Project settings dialog.
- Shopping split into internal `Расчёт и фасовка` and `Чек-лист` tabs.
- Existing Menu, Shopping, Purchase, Equipment, and Documents widgets remain owners of their API and mutation behavior.
- Global navigation uses a temporary drawer below the Material UI `md` breakpoint instead of keeping a permanent sidebar on tablets.
- Purchase checklist controls remain stacked through tablet widths and become horizontal only on desktop.
- Project workspace root prevents horizontal overflow while section tabs retain internal scrolling.
- Module visibility still controls Shopping, Equipment, and Documents sections.

## Explicit non-goals

- no Backend endpoint or schema change;
- no Alembic migration; accepted head remains `h10021`;
- no calculation, preparation, Recipe selection, authorization, document-content, or download-contract change;
- no new Project or Menu capability;
- no audit instrumentation; TH-0094 remains a separate task and pull request;
- no multi-tenancy, microservice, or external runtime service.

## Acceptance evidence

- Frontend unit tests cover section normalization, route generation, and tablet checklist direction.
- Production TypeScript/Vite build succeeds.
- Full Frontend browser acceptance succeeds.
- Responsive AppLayout browser acceptance verifies:
  - closed temporary drawer and no horizontal overflow at 360 px;
  - temporary drawer behavior and no horizontal overflow at 831 px;
  - one permanent sidebar and no horizontal overflow at 1280 px.
- Guided Release acceptance still completes Project creation, Menu generation, Project preparation, reload persistence, full-package download, and mobile overflow verification.
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness succeed on the PR head.

## Result

The Project page is now a navigable work area rather than one long landing page. The released v0.1.0 business and persistence baseline is unchanged.
