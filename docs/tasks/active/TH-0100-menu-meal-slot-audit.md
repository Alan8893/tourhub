# TH-0100 — Menu Generation and MealSlot Audit Coverage

Status: IN PROGRESS

Started: 2026-07-19

## Goal

Add semantic actor-attributed audit coverage to menu generation/regeneration and manual MealSlot dish changes without changing generation behavior.

## Scope

- `meal_plan_generated` shares one transaction with MealPlan persistence and existing equipment refresh;
- generation audit distinguishes initial generation from regeneration and records bounded counts/warnings;
- `meal_slot_dish_added`, `meal_slot_dish_removed`, and `meal_slot_dish_replaced` share the existing derived purchasing/checklist/equipment recalculation transaction;
- all events use the authenticated preparation actor;
- failed generation, mutation, derived refresh, or audit recording leaves neither domain changes nor an AuditEvent;
- existing Administrator Audit API/UI exposes Russian menu and MealSlot labels.

## Out of scope

- Project, settings, mail, invitations, catalogue/import, shopping, equipment, or document audit expansion;
- changing generator algorithms, role rules, variants, preserved-slot behavior, or purchasing calculations;
- ORM-wide audit, undo, replay, export, retention, or external integrations;
- migrations, architecture changes, new menu capabilities, or release-tag movement.

## Definition of done

- generation/regeneration and all three manual MealSlot operations create semantic events in the owning transaction;
- before/after/context data identify Project, MealPlan, slot, selected Dish/Recipe, preserved manual state, and bounded result counts;
- service/API tests cover success, actor attribution, rollback, and unchanged generation/manual behavior;
- real-Chrome Audit acceptance shows Russian labels and filtering without mobile overflow;
- all repository workflows pass on one exact final head;
- current documentation and task state are synchronized before squash merge.
