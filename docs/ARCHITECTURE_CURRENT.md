# TourHub Current Architecture

Status: Active

Last updated: 2026-07-18

## Deployment

- One installation represents one tourist club.
- Multi-tenancy and microservices are prohibited.
- TourHub is a modular monolith with PostgreSQL in production; SQLite is test-only.
- Release images run without application source bind mounts.
- PostgreSQL and Redis remain internal to the release network.

## Application boundaries

Frontend owns presentation, responsive navigation, form state, isolated previews, local display mode, authenticated-user state, route guards, module-visibility rendering, and API integration. It does not own calculations, generation, import validation, settings policy, credential verification, session validity, permissions, document snapshots, or backend authorization.

Backend owns project/menu/catalogue validation, transactional import, shopping/equipment recalculation, document generation inputs, typed settings validation, identity persistence, password verification, session lifecycle, settings authorization, optimistic versions, PostgreSQL row locks, contrast rules, module dependencies, invitation-domain normalization, mail-metadata validation, environment-status projection, and safe focused history.

Engines receive prepared immutable inputs and do not query HTTP, React, settings, identity, or database sessions while calculating or rendering.

## Domain boundaries

### Access — TH-0080 / draft PR #90

ADR-015 defines the first operational identity boundary:

- singleton `IdentityState` serializes one-time bootstrap;
- bootstrap creates exactly one initial Administrator;
- `User` supports Administrator, Instructor, and Verified Instructor role values;
- passwords are stored only as salted standard-library `scrypt` hashes;
- bootstrap/login generate opaque random session tokens;
- the browser receives the token in an HttpOnly SameSite=Lax cookie;
- PostgreSQL stores only the SHA-256 token hash, user, expiry, revocation, and activity timestamps;
- logout revokes the server session and clears the cookie;
- invalid login uses one generic response;
- every System Settings API and `/settings` require Administrator.

Functional invitation rows, user administration, role changes, password reset, broader preparation authorization, and real actor propagation are follow-up Access slices. Existing preparation routes remain available in TH-0080; frontend guards do not replace later backend authorization.

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
- `ModuleSettings` owns presentation visibility only. Hidden modules keep routes and APIs available because visibility is not authorization.
- `InvitationSettings` owns future policy only and creates no invitation rows.
- `MailSettings` owns non-secret future SMTP metadata only and does not send email.

### Settings concurrency and history

Each persisted section saves independently. Updates carry the editor version, serialize with a row lock, and return HTTP 409 when stale.

Focused history stores section, actor label, action, changed field names, resulting version, and timestamp. The latest 200 rows are retained. Binary data, addresses, domain values, imported payloads, footer contents, credentials, raw session tokens, and external values are excluded. TH-0080 does not yet replace the local actor label with the authenticated user; that remains part of actor-aware history work.

### Preparation domains

Project is the preparation root. MealSlot and MealSlotDish are primary; MealPlanItem is compatibility-only. Manual menu choices remain authoritative. Participant changes preserve dishes and transactionally recalculate quantities, shopping, packaging, and equipment.

Dish owns role/meal-type compatibility. Shopping owns aggregation and packaging/checklist state. Equipment owns maximum-simultaneous requirements and project overrides. Documents use one frozen club/document snapshot per generation request.

## Persistence

- Alembic must have exactly one head.
- `main` ends at `h10013`; draft PR #90 adds additive `h10014`.
- Applied migrations are not rewritten.
- Public API placeholders are prohibited.
- Identity and settings require typed ownership, validation, migration, and explicit security boundaries.

## Security

- Backend authorization is authoritative.
- Module visibility is never authorization.
- Invitation policy is not a functional invitation system.
- Mail configuration is not a delivery system.
- Password plaintext and raw session tokens never appear in normal APIs, logs, settings history, diagnostics, or unencrypted exports.
- SMTP values use external/write-only handling.
- Broader preparation authorization and request-forgery hardening remain explicit follow-up work.
- Alcohol prohibition remains approved scope and still requires centralized backend enforcement.

See ADR-012, ADR-013, ADR-014, ADR-015, and `PRODUCT_SPEC.md`.
