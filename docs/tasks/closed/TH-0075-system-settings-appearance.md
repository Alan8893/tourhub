# TH-0075 — System Settings Appearance

Status: DONE

Last updated: 2026-07-17

## Goal

Add a typed site-appearance section to `/settings` that lets one club configure safe light and dark visual themes while each browser chooses `system`, `light`, or `dark` display mode independently.

## Delivered

- independently typed singleton `AppearanceSettings` persistence;
- additive Alembic revision `h10009` with one head;
- complete organization light and dark design-token sets;
- safe fonts, density, radius, button/card styles, and shadow controls;
- TourHub, Forest, Ocean, and Sunset presets plus manual customization;
- backend color and contrast validation with Russian explanations;
- global dynamic MUI theme application without restart;
- per-browser `system` / `light` / `dark` preference in localStorage;
- isolated live preview for unsaved drafts;
- reset, cancel, copy, validated JSON import, and JSON export;
- optimistic versioning, PostgreSQL row locking, HTTP 409 conflicts, and safe focused history;
- desktop/mobile browser acceptance and full exact-head Quality coverage.

## Merge

PR #85 passed Quality #537, Document Quality #164, Guided Release Acceptance #115, Operator Docs #101, and Docker Release Runtime #96, then merged as `0e4e376470072e9475a31504faeb46e8b5a68364`.

## Boundaries retained

Document appearance, module visibility, invitation policy, access, and mail remain independent later slices. Arbitrary CSS, uploaded fonts, remote font URLs, and per-user custom colors remain prohibited.