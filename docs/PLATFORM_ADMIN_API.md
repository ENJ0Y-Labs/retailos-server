# Platform administration read API

All endpoints in this document are platform-level and read-only. They are not
store-owner endpoints. Every request requires a valid session belonging to a
user whose server-managed `users.platform_role` is `admin`. Missing or invalid
sessions return HTTP 401; authenticated non-admin users receive HTTP 403.

The APIs never return password hashes, passwords, session identifiers,
session versions, or authentication tokens. They do not expose shop-level
sales lines, receipts, customer ledgers, or operational records.

## Pagination

Both collection endpoints use server-side pagination:

- `page`: positive integer, default `1`.
- `per_page`: integer from `1` to `100`, default `20`.

Collection responses contain `items` and `pagination` with `page`,
`per_page`, `total`, `pages`, `has_next`, and `has_previous`.

## GET /admin/overview

Returns platform metrics aggregated by the database. It does not download
individual records to the frontend.

Metrics:

- `users_total`: all registered user accounts.
- `stores_total`: all stores.
- `active_premium_stores`: Pro stores whose subscription status is
  `active` or `trial` and whose `current_period_end` is null or in the
  future. An expired period is never counted as active premium.
- `active_trial_stores`: Pro stores with `trial` status and a null or
  future `current_period_end`.
- `free_stores`: stores whose persisted `current_plan` is `free` or null.
  This is a stored-plan count, not a count of expired Pro rows.
- `new_users_last_30_days` and `new_stores_last_30_days`: records created
  in the rolling 30 days before `generated_at`.
- `sales_last_30_days`: count of persisted sales created in the rolling
  30 days. This is a transaction count, not revenue.

The response includes `generated_at` and a `definitions` object so the
frontend can label the metrics accurately.

## GET /admin/users

Optional query parameters:

- `search`: case-insensitive match against user name or email.
- `has_store`: `true` or `false`.
- `plan`: `free` or `pro`; matches a user's associated store plan.
- `sort_by`: `created_at` (default), `name`, `email`, or `id`.
- `sort_order`: `asc` or `desc` (default).

Each user includes `id`, `name`, `email`, `created_at`, `stores_count`,
and associated store summaries. Store summaries include the store ID/name
and subscription plan/status/period end/trial-used/effective-premium fields.

## GET /admin/users/{id}

Returns a user with registration timestamp and associated stores. Each store
includes subscription information and aggregate activity counts:
`products_count`, `customers_count`, `sales_count`, and `last_sale_at`.
No sale details or customer ledger data is returned.

## GET /admin/stores

Optional query parameters:

- `search`: case-insensitive match against store name or owner name/email.
- `plan`: `free` or `pro`.
- `subscription_status`: `active`, `trial`, or `expired`. The `expired` filter uses a non-null period end at or
  before the current UTC instant.
- `sort_by`: `created_at` (default), `name`, `id`, or `plan`.
- `sort_order`: `asc` or `desc` (default).

Each store includes registration timestamp, owner ID/name/email, and
subscription summary. Search, filtering, sorting, and pagination execute
server-side.

## GET /admin/stores/{id}

Returns store registration, owner, subscription summary, and aggregate
activity: product count, customer count, sale count, open alert count, and
last sale timestamp. It does not return individual sales, products, receipts,
or customer ledger entries.

## Errors

- `401 SESSION_NOT_FOUND` or `SESSION_INVALIDATED`: sign in again.
- `403 PLATFORM_ADMIN_REQUIRED`: the account is not a platform administrator.
- `400 VALIDATION_ERROR`: unsupported filters, sort fields, or pagination.
- `404 USER_NOT_FOUND` / `STORE_NOT_FOUND`: requested record does not exist.

Successful responses follow the standard `success/message/data` response
envelope used by the rest of the API.
## Administrator profile and security settings

### GET /admin/profile

Returns the authenticated platform administrator's own profile:

- `id`, `name`, `email`, `platform_role`, and `created_at`.

The response never includes password hashes, password values, or session-version internals.

### PATCH /admin/profile

Updates the authenticated administrator's display name only.

Request:

    {
        "name": "RetailOS Operator"
    }

The name is trimmed and must contain 2 to 100 characters. The endpoint rejects unknown fields, including `email`, `platform_role`, and `password`. Email changes are not supported because the current account model has no email-verification workflow. Password changes must use the existing `POST /auth/change-password` flow.

A real name change creates a `platform_admin.profile_updated` audit event in the same transaction. The event records the administrator, target user, changed field, and previous/new display name. Repeating the existing name is idempotent and does not create another audit event.

### POST /admin/sessions/revoke-all

Revokes every active session belonging to the authenticated administrator. No request body is required or accepted; supplying a target user ID returns `400 VALIDATION_ERROR`. The endpoint cannot revoke another administrator's sessions.

The endpoint increments the current administrator's `session_version`, records a `platform_admin.sessions_revoked` platform audit event in the same transaction, and clears the current browser session. Other signed session cookies for that same administrator are rejected on their next protected request. The administrator must sign in again.

### Session-management limitations

The current authentication system uses Flask's signed client-side session cookie. It stores a user ID and `session_version`; it does not persist individual session records in the database. Therefore:

- There is no `GET /admin/sessions` listing endpoint.
- The API cannot show per-device sessions, creation times, IP addresses, or user agents.
- Individual session revocation is not supported.
- The supported revocation operation is self-service revocation of all sessions through `POST /admin/sessions/revoke-all`.
- The existing password-change endpoint also increments `session_version`, invalidating all sessions for that account.

The API does not simulate a session registry or claim that clearing one browser cookie revokes copied cookies. A future per-session management feature requires a server-side session store with explicit session identifiers and lifecycle records.

Administrator profile changes, administrator password changes, and all-session revocations are written to the append-only platform audit history. Password audit events contain no password material.
