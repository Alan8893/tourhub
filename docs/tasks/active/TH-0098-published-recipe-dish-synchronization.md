# TH-0098 — Published Recipe Dish Synchronization

Status: IN PROGRESS

Started: 2026-07-19

## Goal

Make every newly published CLUB Recipe immediately visible in the Dish catalogue while requiring an explicit human decision before the Dish participates in menu generation.

## Approved behavior

- publication and Recipe-to-Dish synchronization occur in one database transaction;
- if the Recipe is already attached to any Dish, no duplicate relationship or Dish is created;
- otherwise, if an active Dish has exactly the same normalized display name, attach the Recipe as the next variant and keep the existing default and generator settings;
- otherwise create a new active Dish with the Recipe as its default and only variant;
- a newly created Dish has no meal roles and therefore does not participate in role-based autogeneration;
- Dishes with no roles display `Не настроено для генератора` and a direct `Настроить генератор` action;
- Dishes with at least one role display `Готово для генератора`;
- no generator role, meal type, or repeatability value is inferred from Recipe content;
- publication remains audited and row-locked through the existing Recipe lifecycle service.

## Out of scope

- automatic semantic classification of Recipes;
- role suggestions or AI classification;
- Product or Recipe metadata expansion;
- changing existing Dish roles when a same-name Recipe becomes a new variant;
- restoring alcohol-policy archived Dishes;
- database migration or Alembic head change;
- broad audit expansion beyond the existing publication event.

## Definition of done

- publishing a new Recipe creates or attaches exactly one Dish relationship in the same commit;
- transaction failure leaves both Recipe publication and Dish synchronization uncommitted;
- repeated or already-attached publication paths cannot create duplicates;
- exact active-name match attaches the Recipe as a variant without replacing the default or roles;
- a new Dish is listed immediately with zero roles and explicit generator-not-configured UI;
- assigning roles changes the visible state to generator-ready and updates catalogue readiness;
- Backend service/API tests and real-Chrome moderation/Dish tests cover the workflow;
- all repository workflows pass on one exact final head;
- current documentation and task state are synchronized before squash merge.
