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

Frontend owns presentation, responsive navigation, form state, isolated previews, local display mode, authenticated-user state, route guards, manual invitation-link copy UX, user-administration forms, module-visibility rendering, and API integration. It does not own calculations, generation, import validation, settings policy, credential verification, session validity, invitation validity, role invariants, permissions, document snapshots, or backend authorization.

Backend owns project/menu/catalogue validation, transactional import, shopping/equipment recalculation, document generation inputs, typed settings validation, identity persistence, password verification, session lifecycle, invitation lifecycle, user role/activity state, last-Administrator protection, settings authorization, optimistic versions, PostgreSQL row locks, contrast rules, module dependencies, invitation-domain normalization, mail-metadata validation, environment-status projection, and safe focused history.

Engines receive prepared immutable inputs and do not query HTTP, React, settings, identity, or database sessions while calculating or rendering.

## Domain boundaries

### Access bootstrap and sessions — merged TH-0080 / PR #90

ADR-015 defines the first operational identity boundary:

- singleton `IdentityState` serializes one-time bootstrap;
- bootstrap creates exactly one initial Administrator;
- `User` supports Administrator, Instructor, and Verified Instructor role values;
- passwords are stored only as salted standard-library `scrypt` hashes;
- bootstrap/login generate opaque random session values;
- the browser receives the value in an HttpOnly SameSite=Lax cookie;
- PostgreSQL stores only the SHA-256 session hash, user, expiry, revocation, and activity timestamps;
- logout revokes the server session and clears the cookie;
- invalid login uses one generic response;
- every System Settings API and `/settings` require Administrator.

PR #90 merged as `26c4d4eb9246de44579451fe3d6e7bd631538324`.

### Functional invitations — merged TH-0081 / PR #91

ADR-016 defines one-time invitation links:

- only an authenticated Administrator creates, lists, reissues, or revokes invitations;
- each invitation binds one normalized email and one safe non-Administrator role;
- `InvitationSettings` remains the typed policy owner for allowed domains, expiry, active limit, default role, and reissue permission;
- PostgreSQL stores only the non-recoverable invitation-code representation;
- normal lists never reconstruct the link;
- public inspection returns only email, role, and expiry after validation;
- acceptance locks the invitation, rechecks state and policy, creates one user, consumes the invitation, and creates the initial server session in one transaction;
- manual link transfer is the current delivery mechanism; automatic mail remains separate.

PR #91 merged as `2348870864efa1da20547c1a6564dc5f9b6488ef`; `main` ends at Alembic `h10015`.

### User administration — active TH-0082 / draft PR #92

ADR-017 defines user-administration invariants:

- only an authenticated Administrator lists or updates users;
- each user carries a positive optimistic version;
- updates require the expected version and stale writes return HTTP 409;
- updates lock the ordered user set before evaluating role/activity invariants;
- at least one active Administrator must always remain;
- deactivation revokes all active sessions for the target user in the same transaction;
- role changes affect authorization on the next Backend request;
- self-demotion or self-deactivation is allowed only when another active Administrator remains;
- account deletion, password reset, email change, and self-service profile editing remain separate capabilities.

Frontend confirmation is presentation support only. Backend enforcement remains authoritative.

### System Settings

ADR-014 defines one responsive surface with independent typed owners:

```text
/settings
  club         -> ClubSettings
  appearance   -> AppearanceSettings
  documents    -> DocumentAppearanceSettings
  modules      -> ModuleSettings
  users        -> User role/activity administration
  invitations  -> InvitationSettings + Invitation lifecycle
  mail         -> MailSettings

future user
  preferences  -> UserPreferences
```

Unchecked cross-domain JSON and generic key/value storage are prohibited. A bounded homogeneous collection may use JSON only inside its owning typed model.

- `ClubSettings` owns club identity, contacts, approved PNG/JPEG/WebP images, and version.
- `AppearanceSettings` owns organization light/dark design tokens and safe presentation choices.
- `DocumentAppearanceSettings` owns PDF/Excel/print/ZIP palette, logo source, contacts, footer, title image, and density.
- `ModuleSettings` owns presentation visibility only. Hidden modules keep routes and APIs available because visibility is not authorization.
- `InvitationSettings` owns invitation policy; `Invitation` owns operational lifecycle state.
- `User` owns identity, role, active state, and optimistic version.
- `MailSettings` owns non-secret future SMTP metadata only and does not send email.

### Settings concurrency and history

Each persisted settings section saves independently. Updates carry the editor version, serialize with a row lock, and return HTTP 409 when stale.

Focused history stores section, actor label, action, changed field names, resulting version, and timestamp. The latest 200 rows are retained. Binary data, addresses, domain values, imported payloads, footer contents, credentials, raw session values, invitation codes, and external values are excluded. Authenticated actor propagation remains part of later actor-aware history work.

### Preparation domains

Project is the preparation root. MealSlot and MealSlotDish are primary; MealPlanItem is compatibility-only. Manual menu choices remain authoritative. Participant changes preserve dishes and transactionally recalculate quantities, shopping, packaging, and equipment.

Dish owns role/meal-type compatibility. Shopping owns aggregation and packaging/checklist state. Equipment owns maximum-simultaneous requirements and project overrides. Documents use one frozen club/document snapshot per generation request.

## Persistence

- Alembic must have exactly one head.
- `main` ends at `h10015`; draft PR #92 adds additive `h10016`.
- Applied migrations are not rewritten.
- Public API placeholders are prohibited.
- Identity, invitations, users, and settings require typed ownership, validation, migration, and explicit security boundaries.

## Security

- Backend authorization is authoritative.
- Module visibility is never authorization.
- At least one active Administrator must always remain.
- Deactivation invalidates active sessions for the affected user.
- Frontend confirmation never replaces Backend invariants.
- Invitation policy and lifecycle state have separate typed owners.
- Raw session values and invitation codes are not stored in PostgreSQL.
- Mail configuration is not a delivery system.
- Protected values never appear in normal lists, logs, settings history, diagnostics, or unencrypted exports.
- Broader preparation authorization and request-forgery hardening remain explicit follow-up work.
- Alcohol prohibition remains approved scope and still requires centralized backend enforcement.

See ADR-012, ADR-013, ADR-014, ADR-015, ADR-016, ADR-017, and `PRODUCT_SPEC.md`.
