# TH-0071 — Operator Installation and Update Runbook

Status: DONE

Completed: 2026-07-17

Merged PR: #79

Squash commit: `99d9c2d985b8a21c62fe148e07e08b3632ef961a`

## Goal

Provide a safe, executable operator path for installing, updating, backing up, restoring, and recovering the local single-club TourHub MVP.

## Delivered

- installation prerequisites and first-start commands;
- migration, health, LAN, port, and volume verification;
- backup-first application update procedure;
- host-side PostgreSQL custom-format backup command;
- confirmed restore command with an automatic pre-restore safety dump;
- rollback boundaries that prohibit destructive volume deletion and ad hoc production downgrades;
- CI validation for shell syntax, script help, required runbook commands, relative links, and Docker Compose syntax.

## Verified acceptance

- a new operator can start TourHub and verify the API and migration state from the documentation;
- an update procedure creates a backup before rebuilding or migrating;
- restore requires an explicit confirmation flag and leaves application services stopped;
- documentation identifies the `postgres18_cluster_data` persistence boundary;
- README links to both runbooks and operational scripts;
- exact-head Quality #436, Document Quality #67, Guided Release Acceptance #18, and Operator Docs #4 passed before merge.

## Deferred follow-up

- Docker image build and runtime smoke validation;
- PostgreSQL migration upgrade/downgrade smoke;
- release tagging and final release workflow;
- public-internet deployment or multi-tenant hardening.
