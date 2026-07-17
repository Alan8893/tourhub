# TH-0061 — User Project Preparation Wizard

Status: IN PROGRESS

Last updated: 2026-07-16

## Goal

Create a complete guided Russian scenario for preparing a hiking project from creation through final outputs.

## Completed

- project creation, catalogue, workspace, participants, duration, and meal boundaries;
- role-aware menu generation, manual editing, diversity, and warnings;
- purchasing review, packaging, surplus, and purchasing contact through PRs #70–#72;
- recipe equipment requirements and maximum simultaneous aggregation through PR #73;
- project equipment additions, removals, quantity overrides, and recalculation preservation through PR #74;
- transactional refresh after direct recipe-equipment changes through merged PR #75.

## Current slice — draft PR #76

- generate Russian purchase PDF and Excel;
- generate Russian equipment PDF and Excel from final user-facing quantities;
- include calculated baseline and source labels for calculated, overridden, and manual rows;
- exclude removed equipment rows;
- expose dedicated equipment document endpoints;
- provide Russian download controls for purchase, equipment, and the full project package;
- include purchase PDF, purchase Excel, purchase print, equipment PDF, and equipment Excel in the ZIP package;
- verify document contents, API responses, exact browser requests, screenshot, and 360 px layout;
- enforce focused document Ruff, strict mypy, and tests.

Functional head `387185880add5a75dfc59071257f6f93cca33471` passed Quality #389 and Document Quality #23 before documentation synchronization.

## Next

1. Add club name and logo settings and apply document branding.
2. Complete guided desktop and mobile release acceptance.
3. Complete installation, update, Docker build, migration smoke, and release validation.

## Decisions

- Project is the preparation aggregate root.
- Recipe owns simultaneous equipment requirements.
- EquipmentList is a persisted project preparation document.
- Project quantity is the maximum across meal occurrences.
- Calculated quantity remains separate from the final user-controlled quantity.
- Manual additions, removals, and overrides are authoritative during recalculation and export.
- Direct recipe requirement changes update prepared lists transactionally.
- Export uses final visible quantities and excludes removal tombstones.

## Acceptance criteria

- equipment requirements persist and aggregate correctly;
- project equipment remains editable in Russian;
- user decisions survive every recalculation path;
- direct recipe-equipment changes refresh all prepared affected projects;
- Russian purchase and equipment PDF/Excel are downloadable;
- the full package contains purchase and equipment documents;
- desktop and 360 px layouts remain usable;
- all general and document-specific quality gates pass.
