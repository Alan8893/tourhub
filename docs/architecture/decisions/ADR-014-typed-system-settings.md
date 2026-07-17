# ADR-014 — Typed System Settings Ownership

Status: Accepted

Date: 2026-07-17

## Context

TourHub already persists one singleton `club_settings` record for the club name and document logo. The approved product direction requires a dedicated `/settings` area that will eventually cover club identity, site appearance, document appearance, module visibility, invitation policy, outbound mail, and per-user preferences.

Storing all future settings in one unbounded JSON document or generic key/value table would weaken validation, obscure ownership, complicate secret handling, and make conflict detection and migrations unreliable. Conversely, putting every future field into one expanding `club_settings` table would couple unrelated domains and create a settings god object.

One local installation still represents exactly one club. Settings must not introduce multi-tenancy or a new service boundary.

## Decision

### One settings surface, typed section ownership

The frontend exposes one responsive `/settings` surface. Each section owns a typed persistence model, schema, service, API contract, validation rules, version, and history policy.

Planned ownership is:

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

These models may share application-level composition and navigation, but they must not become an arbitrary cross-domain settings dictionary.

### Club settings

`ClubSettings` remains a singleton with `id = 1` and is expanded only with club-identity fields:

- required club name;
- optional short and legal names;
- description, address, phone, email, website, timezone, city, and region;
- a bounded typed collection of labelled social links;
- main, light, and dark logos;
- square icon, favicon, login background, and document image;
- a positive optimistic-concurrency version.

The social-link collection may use a JSON database column because it is one bounded homogeneous value object owned entirely by `ClubSettings`. This does not authorize generic JSON storage for unrelated settings.

Image bytes remain server-owned binary data. The API accepts and returns validated data URLs for the current local MVP, while services validate MIME type, decoded content, dimensions, and per-kind size limits. SVG is not accepted.

### Compatibility

The existing `/api/v1/club-settings` contract remains compatible for current project documents and integrations. The new settings page uses the versioned `/api/v1/settings/club` contract.

Existing document generation continues to consume an immutable branding snapshot built from the main club name and main logo. Light, dark, favicon, login, and document-specific images do not silently alter existing exports until their dedicated slices define that behavior.

### Concurrency

Every typed settings section uses optimistic concurrency. Update requests include the version read by the editor. The backend rejects stale updates with HTTP 409 and never overwrites a newer value silently.

### Change history

Settings history is stored separately from settings state. The first local slice records:

- section;
- actor label;
- action;
- changed field names;
- resulting settings version;
- timestamp.

Until identity exists, the actor label is `Локальный администратор`. The latest 200 settings-history records are retained. Binary data, data URLs, passwords, tokens, and future secrets are prohibited from history metadata and logs.

This focused history does not replace the later actor-aware application audit log. Future authenticated changes will use real actor identity and may be projected into the broader audit system.

### Secrets and configuration archives

Secret-bearing settings are deferred to their owning slices. Mail passwords and similar credentials must use external or write-only secret handling and must never be returned by normal APIs.

A future unencrypted configuration export excludes secrets. A future password-encrypted archive may include explicitly approved secrets, but encryption format, key derivation, integrity protection, and import validation require a separate design and PR.

### User preferences

The organization owns global appearance tokens. Before users exist, a browser may store only the personal light/dark/system mode in local storage. After identity is implemented, that choice moves to typed `UserPreferences`; organization colors, typography, density, and component styling remain global.

## Consequences

- The settings page can grow without coupling every section to `ClubSettings`.
- PostgreSQL and Pydantic retain strong validation for security- and behavior-relevant settings.
- Settings can be saved independently, so a mail error cannot block a club-name update.
- Version conflicts are explicit and testable.
- Existing branding and document behavior remain stable while new appearance slices are introduced.
- Every new settings domain requires an intentional model, migration, API, tests, and ownership decision.
- Configuration export/import must compose multiple typed sections rather than serialize one unchecked blob.

## Rejected alternatives

### One universal `system_settings` row with all columns

Rejected because club identity, appearance, modules, invitations, mail, and user preferences have different validation, lifecycle, secret, and authorization requirements.

### One unrestricted JSON settings document

Rejected because schema drift, partial updates, concurrency, dependency validation, and secret exclusion would be enforced only by convention.

### Generic key/value settings table

Rejected because values lose domain types and ownership, dependencies become implicit, and validation becomes scattered.

### Arbitrary custom CSS

Rejected because it can break responsive layout, accessibility, upgrades, and security assumptions. Appearance customization will use validated design tokens and safe built-in choices.

### Store SMTP passwords as visible database settings

Rejected because secrets must be external or write-only and excluded from normal API responses, logs, history, diagnostics, and unencrypted exports.
