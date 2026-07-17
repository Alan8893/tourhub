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

Frontend owns presentation, responsive navigation, form state, isolated previews, local display mode, module-visibility rendering, and API integration. It does not own calculations, generation, import validation, settings policy, domain normalization, credentials, document snapshots, or authorization.

Backend owns project/menu/catalogue validation, transactional import, shopping/equipment recalculation, document generation inputs, typed settings validation, optimistic versions, PostgreSQL row locks, contrast rules, module dependencies, invitation-domain normalization, mail-metadata validation, environment-status projection, and safe focused history.

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

### InvitationSettings

`InvitationSettings` stores future policy only: expiry, safe default role, optional normalized allowed domains, resend permission, active limit, mandatory administrator-only management, email-confirmation requirement, and optimistic version.

Backend normalizes domains to lowercase ASCII IDNA, removes duplicates, sorts them, and rejects email addresses, schemes, paths, ports, whitespace, and invalid labels. Administrator cannot be the default role; privileged assignment requires a future access-management flow.

This policy does not create users, invitation rows, tokens, emails, acceptance/revocation/resend actions, sessions, or permissions. Access foundation must consume it explicitly.

### MailSettings — draft PR #89

`MailSettings` owns future universal SMTP metadata only:

- SMTP host and port;
- plain, STARTTLS, or TLS connection mode;
- optional username;
- sender email and display name;
- optional Reply-To and test-recipient addresses;
- timeout and retry-count policy;
- optimistic version.

The model has no credential column. Requests accept no credential field. Normal responses expose only:

- whether the external value is configured;
- source `environment`;
- environment variable name `TOURHUB_SMTP_SECRET`;
- `delivery_available = false`;
- `test_delivery_available = false`.

The status is derived on every request, so deployment configuration changes do not require a database migration. Development and release Compose pass the optional value to Backend. The current slice never opens an SMTP connection, verifies credentials, renders mail, queues work, retries delivery, or sends messages. Working delivery begins after identity exists and must consume this metadata explicitly.

### Settings concurrency and history

Each persisted section saves independently. Updates carry the editor version, serialize with a row lock, and return HTTP 409 when stale.

Focused history stores section, local actor, action, changed field names, resulting version, and timestamp. The latest 200 rows are retained. Binary data, addresses, domain values, imported payloads, footer contents, credentials, tokens, and external values are excluded. This is not the future actor-aware audit log.

### Preparation domains

Project is the preparation root. MealSlot and MealSlotDish are primary; MealPlanItem is compatibility-only. Manual menu choices remain authoritative. Participant changes preserve dishes and transactionally recalculate quantities, shopping, packaging, and equipment.

Dish owns role/meal-type compatibility. Shopping owns aggregation and packaging/checklist state. Equipment owns maximum-simultaneous requirements and project overrides. Documents use one frozen club/document snapshot per generation request.

## Persistence

- Alembic must have exactly one head.
- `main` ends at `h10012`; draft PR #89 adds additive `h10013`.
- Applied migrations are not rewritten.
- Public API placeholders are prohibited.
- Settings require typed ownership, validation, migration, concurrency, history, and credential-boundary decisions.

## Security

- Module visibility is never authorization.
- Invitation policy is not a functional access system.
- Mail configuration is not a delivery system.
- Permissions must be enforced by Backend when users exist.
- SMTP credentials use external/write-only handling and never appear in PostgreSQL, update requests, normal APIs, logs, history, diagnostics, UI inputs, or unencrypted exports.
- Alcohol prohibition remains approved scope and still requires centralized backend enforcement.

See ADR-012, ADR-013, ADR-014, and `PRODUCT_SPEC.md`.
