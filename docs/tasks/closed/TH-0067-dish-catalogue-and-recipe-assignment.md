# TH-0067 — Dish Catalogue and Recipe Assignment

Status: DONE

## Goal

Provide a dish catalogue with explicit recipe assignment and safe archived-recipe handling.

## Delivered

- dish list and detail API;
- dish creation and renaming;
- active recipe assignment and replacement;
- dish catalogue and editor frontend;
- historical visibility for an assigned recipe archived later;
- rejection of new archived-recipe assignment;
- duplicate-name validation;
- navigation between dishes and recipes;
- API and frontend regression coverage.

## Persistence boundary

Current persistence stores exactly one selected `recipe_id` per Dish. Multiple recipe variants remain future work.

## Delivery

Implemented through PRs #42 and #43.
