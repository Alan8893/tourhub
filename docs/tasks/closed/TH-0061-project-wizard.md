# TH-0061 — User Project Preparation Wizard

Status: DONE

Completed: 2026-07-17

## Result

TourHub provides a complete guided Russian workflow from project creation through menu generation, purchasing, packaging, equipment, club branding, and final project documents.

Delivered through PRs #70–#78:

- project parameters, participants, duration, and meal boundaries;
- role-aware menu generation and manual editing;
- persisted purchase list, checklist, packaging, surplus, and purchasing contact;
- persisted recipe equipment requirements and maximum-simultaneous project aggregation;
- manual equipment additions, removals, quantity overrides, and recalculation preservation;
- Russian purchase and equipment PDF/Excel plus complete ZIP package;
- singleton club name and verified PNG/JPEG logo branding through Alembic `h10007`;
- persisted preparation readiness restored after browser reload;
- desktop and 360 px create → menu → prepare → reload → branded ZIP acceptance.

## Final verification

- PR #77 merged as `18d4fabde3eda6c83c0c0f998e870a6f043e8dec` after Quality #416 and Document Quality #49.
- PR #78 was retargeted cleanly to `main`, passed Quality #431, Document Quality #63, and Guided Release Acceptance #14, and merged as `6332ef5f86973c7832e92dc1ef0a681cc4e17d1e`.

## Decisions retained

- Project remains the preparation aggregate root.
- Recipe owns simultaneous equipment requirements.
- Calculated equipment quantity remains separate from the final user-controlled quantity.
- Manual additions, removals, and overrides remain authoritative during recalculation and export.
- Club settings are singleton data for the approved one-club MVP.
- One project package uses one immutable branding snapshot.
- Preparation-status reads persisted IDs and never creates or recalculates documents.
