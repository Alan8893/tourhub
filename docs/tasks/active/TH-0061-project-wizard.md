# TH-0061 — User Project Preparation Wizard

Status: IN PROGRESS

Last updated: 2026-07-17

## Goal

Create a complete guided Russian scenario for preparing a hiking project from creation through final outputs.

## Completed

- project creation, catalogue, workspace, participants, duration, and meal boundaries;
- role-aware menu generation, manual editing, diversity, and warnings;
- purchasing review, packaging, surplus, and purchasing contact through PRs #70–#72;
- recipe equipment requirements, project overrides, and transactional recalculation through PRs #73–#75;
- Russian purchase/equipment PDF, Excel, print, download controls, and project ZIP package through merged PR #76.

## Current slice — draft PR #77

- persist one club name and optional logo through Alembic `h10007`;
- accept only verified PNG/JPEG images up to 1 MB and 16 million pixels;
- provide Russian load/edit/preview/remove/save UI;
- use one cached branding snapshot for all files generated in one package;
- show club branding in PDF headers/footers and Excel metadata/header/logo;
- preserve existing purchase and equipment table layouts;
- cover API persistence/removal/validation, branded outputs, exact browser PUT body, screenshot, and 360 px layout;
- enforce branding modules with focused Ruff, strict mypy, and tests.

Functional head `c3f2c2b767a0751bbf11c214e4f07b21176d0be5` passed Quality #412 and Document Quality #45 before documentation synchronization.

## Next

1. Complete guided desktop and mobile release acceptance.
2. Complete installation and update documentation.
3. Add Docker build, migration smoke, and final release validation.

## Decisions

- Project is the preparation aggregate root.
- Recipe owns simultaneous equipment requirements.
- EquipmentList is a persisted project preparation document.
- Calculated quantity remains separate from the final user-controlled quantity.
- Manual additions, removals, and overrides are authoritative during recalculation and export.
- Export uses final visible quantities and excludes removal tombstones.
- Club settings are singleton data for the approved one-club MVP.
- A document package uses one immutable branding snapshot.

## Acceptance criteria

- project preparation from menu through documents works in Russian;
- user purchasing and equipment decisions survive recalculation;
- purchase and equipment documents are downloadable individually and as one package;
- club name and optional logo persist and appear consistently in generated documents;
- invalid or oversized logos are rejected;
- desktop and 360 px layouts remain usable;
- all general and document-specific quality gates pass.
