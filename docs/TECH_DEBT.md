# TourHub Technical Debt

Status date: 2026-07-17

Implemented through merged PR #76:

- equipment requirements, overrides, and recalculation;
- Russian purchase and equipment PDF/Excel;
- complete five-file project ZIP package.

PR #77 addresses branding debt:

- persistent club name and logo through Alembic `h10007`;
- validated PNG/JPEG rendering across PDF, Excel, print, and ZIP;
- Russian settings UI and mobile acceptance.

Stacked PR #78 addresses guided-release debt:

- persisted preparation readiness after reload;
- equipment-aware completion state;
- clean unprepared states instead of false 404 errors;
- full create, menu, prepare, reload, and ZIP browser acceptance;
- focused desktop/mobile evidence and failure diagnostics.

Remaining priorities:

- merge and retarget the PR #77 to PR #78 stack;
- PostgreSQL migration upgrade and downgrade smoke;
- Docker build validation;
- installation and update documentation;
- final release workflow.
