# TH-0109 — Dish Archive Management

Status: IN PROGRESS

## Goal

Allow preparation users to archive and restore Dish catalogue records without deleting Recipes, MealSlot assignments, historical calculations, exports, or audit references, while keeping the lifecycle policy Backend-owned and the existing active Dish catalogue contract stable.

## Scope

- keep the default Dish catalogue active-only and preserve its existing response contract;
- add an explicit protected archive projection exposing lifecycle state needed by the management UI;
- add protected single-Dish archive and restore actions;
- perform soft archive only; never physically delete a Dish or cascade into Recipes and historical project data;
- make archive and restore row-locked, idempotent, and transactionally audited as `dish_archived` and `dish_restored`;
- prevent archived Dishes from being selected for new catalogue assignments while preserving existing historical references;
- expose a responsive active/archive management flow from the existing Dish catalogue UX;
- cover Backend policy, Frontend helpers, real-Chrome behavior, mobile overflow, and exact-head release gates.

## Policy decisions

- archive changes only the Dish lifecycle flag;
- restore is allowed for a manually archived Dish when its stored state still satisfies current validation rules;
- repeated archive or restore requests return the current state without duplicate AuditEvents;
- archived records remain readable only through explicit management or historical-resource paths;
- existing Dish and Recipe API DTOs remain stable; archive-management state uses dedicated schemas;
- state change and semantic audit share one database transaction.

## Non-goals

- Product archive changes;
- Recipe publication, moderation, ownership, or archive lifecycle changes;
- physical deletion or cascading cleanup;
- bulk archive or restore;
- editing an archived Dish;
- ownership-aware CSV import UX;
- audit retention UI, global sign-out, Administrator session administration, session cleanup, or `Копировать проект`;
- multi-tenant support, microservices, or moving immutable tag `v0.1.0`.

## Acceptance

- an active Dish can be archived and disappears from the default active catalogue;
- the archived Dish appears in the explicit archive projection;
- Recipes and existing MealSlot/project references remain intact;
- an archived Dish can be restored and becomes available in the active catalogue again;
- archive and restore are idempotent and emit exactly one audit event per actual transition;
- forced audit failure rolls back the lifecycle change;
- protected endpoints enforce preparation access;
- responsive UI covers loading, empty, success, error, archive, and restore states;
- real Chrome verifies requests, state transitions, reference preservation, and absence of mobile horizontal overflow;
- Backend, Frontend, Product Acceptance, Docker Release Runtime, Document Quality, Guided Release Acceptance, Operator Docs, and Final Release Readiness pass on the exact implementation head.
