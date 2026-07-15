# TH-0069 — Dish Recipe Purchasing Recalculation

Status: DONE

## Goal

Keep persisted purchasing projections consistent when an existing dish is switched to another recipe.

## Delivered

- detection of every MealPlan that currently uses the changed dish;
- transactional refresh of purchase lists and purchase checklists;
- preservation of purchased quantities, checked state, and notes for products that remain;
- no recalculation for name-only dish edits;
- complete rollback when any affected plan cannot be recalculated;
- regression coverage for recipe replacement and purchasing results;
- Ruff and strict mypy coverage for the coordinator service.

## Delivery

Implemented through PR #48.
