# TH-0078 — System Settings Invitation Policy

Status: DONE

Completed: 2026-07-17

Merged in PR #88 as `d79172fef861c030ff2d9e5367cf86329068b460`.

The completed slice added typed future invitation policy through Alembic `h10012`, including expiry, safe default role, normalized allowed domains, resend policy, active limit, mandatory administrator-only management, email confirmation, optimistic concurrency, row locking, safe history, and a responsive Russian editor. It intentionally did not create users, invitation records, tokens, registration, sessions, authorization, SMTP, or email delivery.
