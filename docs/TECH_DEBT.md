# TourHub Technical Debt

Status date: 2026-07-17

The detailed technical-debt register is synchronized with the current project status and roadmap.

Implemented through merged PR #76:

- equipment requirements, aggregation, project overrides, and recalculation;
- Russian purchase and equipment PDF/Excel;
- complete purchase/equipment ZIP package and focused document gates.

Draft PR #77 addresses final document-branding debt:

- persistent single-club name and logo settings;
- strict PNG/JPEG validation and safe rendering;
- consistent branding snapshot across PDF, Excel, print, and ZIP;
- Russian settings UI and mobile browser acceptance.

Remaining priorities:

- final guided release acceptance;
- PostgreSQL migration upgrade/downgrade smoke;
- Docker build validation;
- installation and update documentation;
- final release workflow.
