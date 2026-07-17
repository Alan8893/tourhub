# TourHub Technical Debt

Status date: 2026-07-17

## Implemented through merged PR #86

- complete guided project preparation from creation through branded documents;
- persisted shopping, equipment, overrides, recalculation, and reload-safe readiness;
- installation, update, backup, restore, and recovery runbooks;
- production-like Docker images and release Compose;
- internal PostgreSQL/Redis networking, health checks, API proxy, clean startup, and restart persistence;
- evidence-based product completeness and release sequencing;
- final downgrade/re-upgrade migration smoke deferred until first-release feature freeze;
- dedicated `/settings` surface and responsive section navigation;
- typed singleton club identity through Alembic `h10008`;
- independent site appearance through `h10009`;
- independent document appearance and immutable generation snapshot through `h10010`;
- validated versioned theme JSON import/export without secrets;
- optimistic conflict detection, PostgreSQL row locking, and safe local-admin settings history;
- ADR-014 independent typed settings ownership.

## Active TH-0077 / draft PR #87

The module-visibility slice addresses:

- static sidebar entries with no typed organization visibility policy;
- no visibility controls for shopping, equipment, and document workspace cards;
- no required-module metadata or lock reasons;
- no backend dependency validation between visible documents and their required outputs;
- no independent module settings version/history contract.

Implemented in the draft slice:

- independent typed singleton `module_settings` model and Alembic `h10011`;
- explicit project, catalogue, import, shopping, equipment, and document visibility columns;
- required project/catalogue locks;
- backend document → shopping/equipment dependency validation before mutation;
- database constraints protecting required and dependency states;
- optimistic versioning, row locking, HTTP 409 conflicts, and safe module history;
- typed API metadata with labels, descriptions, dependencies, required state, and Russian lock reasons;
- global frontend visibility provider;
- immediate desktop/mobile sidebar updates after save;
- project shopping/purchase, equipment, and document card visibility;
- responsive module editor and focused browser acceptance;
- direct routes and APIs intentionally remain available.

## Remaining System Settings debt

### Future invitation configuration

- typed expiry, default role, allowed-domain, resend, active-limit, and email-confirmation policy fields;
- no functional invitation list until users and access foundation exist;
- backend validation and safe history without pretending invitations are operational.

### Mail boundary before access

- informative description of universal SMTP ownership and secret handling;
- no working delivery, password persistence, or test message until identity exists.

### Mail after access foundation

- universal SMTP configuration;
- host, port, TLS/STARTTLS, username, sender, Reply-To, timeout, and retry policy;
- password supplied through environment or another write-only secret boundary;
- configured/verified/restart status without returning the secret;
- separate test-recipient field and fixed Russian test email;
- no visual template editor in the first mail slice.

### Configuration export and import

- versioned JSON plus image files in a validated archive;
- unencrypted archive excludes secrets;
- password-encrypted archive may include explicitly approved secrets;
- encryption, key derivation, authenticated integrity, password handling, import preview, and rollback require a separate security design;
- secrets must remain excluded from logs, history, diagnostics, normal API responses, and unencrypted exports.

## Remaining release-blocking product debt

1. **Access foundation**
   - users, invitations, approved roles, authentication, sessions, guarded routes, and backend authorization.
2. **Working mail delivery**
   - connect approved mail settings to identity and invitation flows.
3. **Recipe ownership and lifecycle**
   - CLUB/PERSONAL ownership, multiple variants, submission, review, approval, rejection, publication, archive, and generation modes.
4. **Central alcohol prohibition**
   - one backend rule across Product, Recipe, and CSV import plus reviewed existing-record handling.
5. **Actor-aware audit log**
   - safe history for project, menu, recipe, settings, mail, user, and role changes.
6. **Consolidated export completeness**
   - approved complete Russian PDF and workbook sheets using the implemented immutable brand snapshot.
7. **Product acceptance**
   - active catalogue data, import interaction, optional-scope decisions, and end-to-end scenarios.

## Product Owner decisions still required

- whether preference-based menu priority blocks first release;
- mandatory recipe metadata for first release;
- exact authentication/session mechanism during access-foundation design;
- encrypted settings archive cryptographic format during its dedicated security design.

## Deferred final release debt

Only after first-release feature freeze:

- PostgreSQL previous → head → previous → head migration smoke;
- final production-like deployment checklist;
- final release workflow and release tag.