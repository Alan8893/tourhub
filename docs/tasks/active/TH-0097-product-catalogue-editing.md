# TH-0097 — Product Catalogue Editing

Status: IN PROGRESS

Started: 2026-07-19

## Goal

Allow an authorized preparation user to correct shared Product catalogue settings from the Recipe component workflow without recreating the Product or changing existing RecipeComponent quantities.

## Approved scope

- edit Product name, category, catalogue unit, and package size;
- keep the Product identifier and every existing relationship intact;
- apply the same uniqueness and central alcohol-policy validation used during creation;
- expose the action next to the selected Product in the Recipe component dialog;
- warn that shared Product changes affect every Recipe that references the Product;
- do not convert or rewrite RecipeComponent amount/unit values automatically;
- refresh the Product list and open Recipe after a successful update;
- cover Backend API behavior and real-Chrome desktop/mobile interaction.

## Out of scope

- Product archival or restore UI;
- unit-conversion rules;
- automatic recalculation of existing RecipeComponent values;
- shopping or historical Project snapshot rewrites;
- Product ownership or per-user catalogue variants;
- database migration or Alembic head change;
- automatic Recipe-to-Dish synchronization, which belongs to TH-0098.

## Definition of done

- `PUT /products/{product_id}` updates an active Product and returns the canonical response;
- missing, duplicate-name, and alcohol-policy violations return existing API error boundaries;
- Recipe details immediately expose updated shared Product fields;
- component amount and component unit remain unchanged when Product catalogue unit changes;
- UI supports create and edit modes with responsive controls and explicit shared-impact warning;
- focused Backend tests and Recipe browser acceptance pass;
- all repository workflows are green on the exact PR head;
- current documentation and task index are synchronized before squash merge.
