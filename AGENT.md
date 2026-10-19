# AGENT.md — RetailOS Server

## Purpose
This repository contains the Flask API backend for TX RetailOS. Keep business rules, authorization, validation, persistence, and transactional operations on the server.

## Before changing code
1. Read this file and the relevant sections of `README.md`.
2. Inspect the existing implementation, tests, models, and migration history before editing. Follow established patterns unless there is a clear reason not to.
3. Keep changes focused on the requested task. Do not silently expand scope or rewrite unrelated code.
4. Never commit secrets, credentials, production data, or local environment files.

## Architecture and data integrity
- Keep route/controller code thin; place business logic in the existing service layer where appropriate.
- Enforce authentication, store-level authorization, and input validation on the server. Never trust client-supplied totals, permissions, or stock values.
- Sales, stock deductions, inventory movements, customer balances, and related records must remain consistent. Use database transactions and preserve rollback behavior.
- Preserve sale idempotency using `client_transaction_id` where supported. A retry must not create a duplicate sale.
- Keep stock quantities in each product's configured base unit. Validate conversions and quantities before applying inventory changes.
- Use consistent error response shapes and meaningful error codes; avoid leaking secrets or internal exception details.
- Store timestamps consistently in UTC and apply the `Africa/Lagos` day boundary when calculating Nigerian business-day reports, as required by the existing API contract.
- Avoid introducing ORM patterns or dependencies that conflict with the existing SQLAlchemy/service design.

## Database migrations
- Never edit or delete an already-applied migration merely to make a new schema change work.
- Inspect the migration graph before adding migrations. If multiple heads exist, confirm the graph and use an explicit merge migration when appropriate.
- New migrations must be reversible when practical and safe for existing data.
- Verify both a fresh database setup and an upgrade from the previous supported schema when changing migrations.

## Testing and verification
Run commands from the repository root unless the project setup requires otherwise:
- Install dependencies: `pip install -r server/requirements.txt`
- Run backend tests: `pytest server/tests`
- Inspect migration heads when migrations change: `flask --app server.app db heads` (set the required environment variables first).
- Add or update regression tests for bug fixes, validation, authorization, transaction rollback, stock protection, and idempotency as relevant.
- Do not claim a test passed unless you actually ran it. Report commands that could not be run and why.

## Completion checklist
- [ ] Existing behavior and API contract were checked before editing.
- [ ] Validation, authorization, and transaction boundaries are correct.
- [ ] Relevant tests were added or updated.
- [ ] Relevant tests and migration checks were run, with results reported.
- [ ] No secrets or unrelated changes were included.
- [ ] The final summary explains what changed, files affected, tests run, and any remaining risks.
