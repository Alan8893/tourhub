# TH-0098 — Published Recipe Dish Synchronization

Status: DONE

Started: 2026-07-19

Completed: 2026-07-19

Pull request: #108

## Goal

Make every newly published CLUB Recipe immediately visible in the Dish catalogue while requiring an explicit human decision before the Dish participates in menu generation.

## Delivered behavior

- Recipe publication, Dish synchronization, and the existing publication AuditEvent share one SQLAlchemy transaction;
- the synchronization service never commits independently;
- if the Recipe is already a Dish default or variant, no duplicate relationship or Dish is created;
- if an active Dish has the exact same name, the Recipe is appended as the next ordered variant while preserving the current default and all generator roles;
- otherwise one active Dish is created with the Recipe as its default and only variant;
- publication-created Dishes have no meal roles and do not participate in role-based generation;
- role-less Dishes display `Не настроено для генератора` and expose `Настроить генератор`;
- role-configured Dishes display `Готово для генератора` and contribute to catalogue readiness;
- no role, meal type, or repeatability value is inferred from Recipe content;
- successful publication invalidates Recipe and Dish frontend queries;
- no database migration was added and Alembic remains `h10021`.

## Verification

- service tests prove new-Dish creation, idempotency, exact-name variant attachment, default/role preservation, and rollback after a post-flush synchronization failure;
- API acceptance proves publication creates one role-less Dish and readiness reports it as unclassified;
- existing Dish API/readiness tests now use publication-created Dishes where appropriate;
- strict Ruff and mypy baselines include both the synchronization service and Recipe lifecycle service;
- unit tests cover generator readiness labels;
- focused real-Chrome Product Acceptance proves the warning, direct setup action, explicit main/dinner role assignment, ready-state transition, request payload, and 360 px overflow boundary;
- Product Acceptance, Quality, Document Quality, Guided Release Acceptance, Operator Docs, Docker Release Runtime, and Final Release Readiness all passed on candidate head `690e63bafab437672eb39185789ddc51fba951f3`;
- the final exact-head workflow run is required after documentation closure before squash merge.

## Preserved boundaries

- no automatic Recipe classification, role suggestion, or AI inference;
- no change to an existing same-name Dish's default Recipe or roles;
- no restoration of archived Dishes;
- no Product/Recipe metadata expansion;
- no architecture, runtime, database, Alembic, or v0.1.0 tag change.
