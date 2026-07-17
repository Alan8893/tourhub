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

## Review stack

### PR #77 — persistent club branding

- persist one club name and optional verified PNG/JPEG logo through Alembic `h10007`;
- provide Russian load/edit/preview/remove/save UI;
- use one immutable branding snapshot for all files generated in one package;
- show club branding in PDF and Excel without shifting existing tables;
- cover API validation, branded outputs, exact browser PUT body, screenshot, and 360 px layout.

PR #77 exact head `317d3b013e0a24c224c8b291e06f49bef349305d` passed Quality #416 and Document Quality #49 and is Ready.

### Stacked PR #78 — final guided release acceptance

- expose persisted preparation readiness without changing derived documents;
- restore meal plan, purchase list, checklist, equipment, and document readiness after reload;
- require equipment before marking the project and documents complete;
- treat absent purchase/checklist/equipment documents as normal unprepared states;
- localize the remaining project-workspace text;
- verify the full application flow from project creation through branded ZIP download;
- assert exact create/generate/prepare/status/package requests;
- capture desktop execution, mobile screenshot, and 360 px no-overflow;
- enforce the flow in a focused Guided Release Acceptance workflow.

Functional PR #78 head `b247b2d7c2dd38c9874e92c524a66f25b293e3bf` passed Quality #421, Document Quality #54, and Guided Release Acceptance #5 before documentation synchronization.

## Next

1. Merge PR #77.
2. Retarget or rebase PR #78 onto `main`, rerun exact-head checks, and merge it.
3. Move TH-0061 to completed tasks.
4. Complete installation/update documentation, Docker build, migration smoke, and final release validation.

## Decisions

- Project is the preparation aggregate root.
- Recipe owns simultaneous equipment requirements.
- EquipmentList is a persisted project preparation document.
- Calculated quantity remains separate from the final user-controlled quantity.
- Manual additions, removals, and overrides are authoritative during recalculation and export.
- Export uses final visible quantities and excludes removal tombstones.
- Club settings are singleton data for the approved one-club MVP.
- A document package uses one immutable branding snapshot.
- Preparation status reads persisted IDs and never creates or recalculates documents.

## Acceptance criteria

- project preparation from creation through documents works in Russian;
- user purchasing and equipment decisions survive recalculation;
- purchase and equipment documents are downloadable individually and as one package;
- club name and optional logo persist and appear consistently in generated documents;
- invalid or oversized logos are rejected;
- prepared state survives a full browser reload without repeated preparation;
- equipment is required before final completion is shown;
- desktop and 360 px layouts remain usable;
- general, document, and guided-release quality gates pass.
