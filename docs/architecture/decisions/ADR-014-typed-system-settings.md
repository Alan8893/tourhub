# ADR-014 — Typed System Settings Ownership

Status: Accepted

Date: 2026-07-17

## Context

TourHub needs one `/settings` area for club identity, site appearance, document appearance, module visibility, invitation policy, outbound mail, and future per-user preferences.

One unrestricted JSON document, a generic key/value table, or an ever-growing `club_settings` table would weaken validation, hide ownership, complicate migrations and concurrency, and make secret handling unsafe. One local installation still represents exactly one club; settings do not introduce multi-tenancy or a service boundary.

## Decision

### One surface, independent typed owners

```text
/settings
  club         -> ClubSettings
  appearance   -> AppearanceSettings
  documents    -> DocumentAppearanceSettings
  modules      -> ModuleSettings
  invitations  -> InvitationSettings
  mail         -> MailSettings

future authenticated user
  preferences  -> UserPreferences
```

Each section owns its persistence model, schema, service, API, validation, optimistic version, row-lock behavior, and history policy. Sections may share UI composition but may not become an unchecked cross-domain dictionary.

### Club settings

`ClubSettings` owns only club identity: required name, optional profile/contact/location data, bounded labelled social links, approved image roles, and version. The social-link JSON column is permitted because it is one bounded homogeneous value object. Image bytes remain server-owned; PNG/JPEG/WebP are validated and SVG is rejected.

### Appearance and documents

`AppearanceSettings` owns organization-wide light/dark design tokens and safe built-in presentation choices. `DocumentAppearanceSettings` independently owns PDF/Excel/print/ZIP palette, approved logo source, contacts, footer, title image, and density. Arbitrary CSS, uploaded fonts, remote resources, rich markup, and per-project themes remain prohibited.

### Module settings

`ModuleSettings` owns presentation visibility only. Required modules and dependencies use explicit columns and backend/database checks. Hiding a module does not remove routes, disable APIs, unload backend code, authorize requests, or delete data.

### Invitation settings

`InvitationSettings` stores policy for the later access implementation, not invitations themselves:

- expiry from 1 to 90 days;
- default role limited to Instructor or Verified Instructor;
- optional allowed email domains;
- resend permission;
- active invitation limit from 1 to 1000;
- mandatory administrator-only management;
- email-confirmation requirement;
- optimistic version.

Allowed domains are a bounded homogeneous list owned by this model, so a JSON column is acceptable. The backend normalizes entries to lowercase ASCII IDNA, removes duplicates, sorts them, and rejects email addresses, schemes, paths, ports, whitespace, and invalid labels. An empty list means any domain.

Administrator is intentionally not available as a default invitation role. Privileged role assignment requires an explicit future access-management flow. The administrator-only rule is protected by both request validation and a database constraint.

This policy does not create User or Invitation rows, tokens, acceptance/revocation/resend execution, mail delivery, sessions, or permissions. Access foundation must consume the policy explicitly when those domains are implemented.

### Compatibility

The legacy `/api/v1/club-settings` contract remains compatible. Versioned settings APIs are section-specific under `/api/v1/settings/...`. Existing project and document routes remain unchanged.

### Concurrency and history

Every typed settings update includes the version read by the editor. The backend serializes writes with a PostgreSQL row lock and rejects stale updates with HTTP 409.

Focused history stores section, local actor label, action, changed field names, resulting version, and timestamp. Until identity exists, the actor is `Локальный администратор`. The latest 200 rows are retained. Binary data, data URLs, domain values, imported payloads, passwords, tokens, and secrets are excluded from history metadata and logs. This does not replace the later actor-aware audit log.

### Secrets and configuration archives

Secret-bearing settings belong to their own slices. Mail passwords and similar credentials use external or write-only handling and are never returned by normal APIs.

Unencrypted configuration exports exclude secrets. A password-encrypted archive may include explicitly approved secrets only after a dedicated design defines encryption, key derivation, authenticated integrity, password handling, preview, validation, and rollback.

### User preferences

The organization owns global appearance. Before users exist, a browser stores only `system`, `light`, or `dark`. After identity exists, that choice moves to typed `UserPreferences`; organization colors and component styling remain global.

## Consequences

- PostgreSQL and Pydantic retain strong domain validation.
- Settings save independently and conflicts are explicit.
- Invitation policy can be prepared without pretending access exists.
- Every settings domain requires an intentional model, migration, API, tests, and secret boundary.
- Full configuration transfer composes typed sections rather than serializing one unchecked object.

## Rejected alternatives

- one universal settings row with unrelated columns;
- one unrestricted JSON settings document;
- generic key/value storage;
- arbitrary custom CSS;
- visible database storage for SMTP passwords;
- allowing Administrator as the default invitation role.
