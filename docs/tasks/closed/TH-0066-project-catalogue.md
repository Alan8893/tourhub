# TH-0066 — Project Catalogue

Status: DONE

## Goal

Provide a real project list at `/projects` and keep individual preparation workspaces at `/projects/{id}`.

## Delivered

- project list query and frontend state;
- responsive project cards;
- status, date, duration, participant count, and meal-boundary summary;
- navigation to individual workspaces;
- entry point for creating a new project;
- removal of the implicit fallback to project `1` when no route ID is present.

## Verification

- frontend production build and automated gates pass;
- `/projects` and `/projects/{id}` have separate route responsibilities.

## Delivery

Implemented through PR #44.
