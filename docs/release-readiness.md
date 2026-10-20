# TX RetailOS server release-readiness notes

Date: 2026-10-20

## Repository evidence

- `AGENT.md` identifies this repository as the Flask API and places business rules, store authorization, validation, persistence, and transactional operations on the server.
- `README.md` documents PostgreSQL configuration, cookie/CORS settings, and the pytest suite.
- `pytest.ini` sets `server/tests` as the test directory.
- `.github/workflows/tests.yml` provisions PostgreSQL, checks that the Alembic graph has exactly one head, upgrades an empty database, and runs the backend test job.
- The server README explicitly states that login rate limits use per-IP and per-IP/email limits and that `memory://` storage is only appropriate for local development/single-process tests. Production should use a shared Redis instance.
- The server README states that session-cookie authentication is used and that `Authorization` and `X-CSRF-Token` headers are not validated by the current API.

## Required production checks

- [ ] Confirm the deployed service uses PostgreSQL and the expected current Alembic revision.
- [ ] Confirm `SECRET_KEY` is strong, private, and stable across service instances.
- [ ] Confirm `RATELIMIT_STORAGE_URI` points to a reachable shared Redis service in production, not `memory://`; verify limits behave correctly across workers/instances.
- [ ] Inspect `ProxyFix` and the actual hosting proxy chain. Ensure forwarded client IPs are trusted only from known proxy hops and cannot be spoofed by direct clients.
- [ ] Verify the exact `FRONTEND_URL`/`CORS_ORIGINS`, cookie `Secure` and `SameSite` settings, and the production HTTPS/session flow through the client's same-origin rewrite.
- [ ] Capture the server GitHub Actions result for the release commit, including migration checks and PostgreSQL-backed tests.
- [ ] Exercise store isolation, invalid/expired sessions, invalid quantities, insufficient stock, transaction rollback, duplicate sale IDs, receipts, outstanding balances, alerts, and dashboard business-day boundaries.

## Migration safety

Do not edit or delete applied Alembic migrations. Inspect the full migration graph and upgrade/downgrade behavior. The CI workflow already includes a migration-head check and fresh-database upgrade; ensure the release CI result confirms these steps pass.

## Current assessment

**Not yet verified for release.** These notes reflect repository configuration and documentation, not access to live Render/Redis settings or a production test. A documented Redis recommendation is not proof that Redis is configured. Attach actual CI and production smoke-test evidence before declaring the server release-ready.
