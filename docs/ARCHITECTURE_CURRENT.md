# TourHub Current Architecture

Status: Active

Last updated: 2026-07-17

## Deployment

- One installation represents one tourist club.
- Multi-tenancy and microservices are prohibited.
- TourHub is a modular monolith with PostgreSQL in production; SQLite is test-only.
- Release images run without application source bind mounts.
- PostgreSQL and Redis remain internal to the release network.

## Application boundaries

Frontend owns presentation, responsive navigation, form state, isolated previews, local display mode, module-visibility rendering, and API integration. It does not own calculations, generation, import validation, settings policy, domain normalization, secrets, document snapshots, or authorization.

Backend owns project/menu/catalogue validation, transactional import, shopping/equipment recalculation, document generation inputs, typed settings validation, optimistic versions, PostgreSQL row locks, contrast rules, module dependencies, invitation-domain normalization, and safe focused history.

Engines receive prepared immutable inputs and do not query HTTP, React, settings, or database sessions while calculating or rendering.

## Domain boundaries

### Access — deferred

Invitation-only access and Administrator, Instructor, and Verified Instructor roles are approved but not operational. User/Invitation persistence, tokens, login, sessions, route guards, and permissions do not exist yet. `/settings` remains locally accessible and will become Administrator-only after access foundation.

### System Settings

ADR-014 defines one responsive surface with independent typed owners:

```text
/settings
  club         -> ClubSettings
  appearance   -> AppearanceSettings
  documents    -> DocumentAppearanceSettings
  modules      -> ModuleSettings
  invitations  -> InvitationSettings
  mail         -> MailSettings

future user
  preferences  -> UserPreferences
```

Unchecked cross-domain JSON and generic key/value storage are prohibited. A bounded homogeneous collection may use JSON only inside its owning typed model.

- `ClubSettings` owns club identity, contacts, approved PNG/JPEG/WebP images, and version.
- `AppearanceSettings` owns organization light/dark design tokens and safe presentation choices.
- `DocumentAppearanceSettings` owns PDF/Excel/print/ZIP palette, logo source, contacts, footer, title image, and density.
- `ModuleSettings` owns presentation visibility only. Projects/catalogue are required; visible documents require visible shopping/equipment. Hidden modules keep routes and APIs available because visibility is not authorization.

### InvitationSettings — PR #88

`InvitationSettings` stores future policy only:

- expiry from 1 to 90 days;
- default role limited to Instructor or Verified Instructor;
- optional allowed email domains;
- resend permission;
- active invitation limit from 1 to 1000;
- mandatory administrator-only management;
- email-confirmation requirement;
- optimistic version.

Backend normalizes domains to lowercase ASCII IDNA, removes duplicates, sorts them, and rejects email addresses, schemes, paths, ports, whitespace, and invalid labels. An empty list means any domain. Administrator cannot be the default role; privileged assignment requires an explicit future access-management flow. Administrator-only is enforced by request validation and PostgreSQL constraints.

This policy does not create users, invitation rows, tokens, emails, acceptance/revocation/resend actions, sessions, or permissions. Access foundation must consume it explicitly.

### Settings concurrency and history

Each section saves independently. Updates carry the editor version, serialize with a row lock, and return HTTP 409 when stale.

Focused history stores section, local actor, action, changed field names, resulting version, and timestamp. The latest 200 rows are retained. Binary data, data URLs, domain values, imported payloads, footer contents, passwords, tokens, and secrets are excluded. This is not the future actor-aware audit log.

### Preparation domains

Project is the preparation root. MealSlot and MealSlotDish are primary; MealPlanItem is compatibility-only. Manual menu choices remain authoritative. Participant changes preserve dishes and transactionally recalculate quantities, shopping, packaging, and equipment.

Dish owns role/meal-type compatibility. Shopping owns aggregation and packaging/checklist state. Equipment owns maximum-simultaneous requirements and project overrides. Documents use one frozen club/document snapshot per generation request.

## Persistence

- Alembic must have exactly one head.
- `main` ends at `h10011`; PR #88 adds additive `h10012`.
- Applied migrations are not rewritten.
- Public API placeholders are prohibited.
- Settings require typed ownership, validation, migration, concurrency, history, and secret-boundary decisions.

## Security

- Module visibility is never authorization.
- Invitation policy is not a functional access system.
- Permissions must be enforced by Backend when users exist.
- Mail credentials use external/write-only handling and never appear in normal APIs, logs, history, diagnostics, or unencrypted exports.
- Alcohol prohibition remains approved scope and still requires centralized backend enforcement.

See ADR-012, ADR-013, ADR-014, and `PRODUCT_SPEC.md`.
