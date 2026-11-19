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


## GET /admin/subscriptions

Returns a paginated, read-only list of store subscription entitlements.

Optional query parameters:

- `state`: `free`, `trial`, `active`, or `expired`.
- `plan`: `free` or `pro`.
- `search`: case-insensitive match against store name or owner name/email.
- `sort_by`: `created_at` (default), `name`, `id`, `plan`, `status`, or `period_end`.
- `sort_order`: `asc` or `desc` (default).

Each item contains account and store summaries plus the effective subscription
entitlement. An expired Pro period is reported as expired even when the stored
plan/status fields have not yet been normalized. Free stores are reported as
Free; trial and active Pro states require a non-expired period.

The current data model has no authoritative subscription-payment record.
Payment status is therefore omitted rather than inferred from a plan or
subscription request. No payment credentials are returned.

## GET /admin/subscription-requests

Returns paginated plan-change requests. Optional query parameters:

- `status`: `pending` or `cancelled`.
- `search`: case-insensitive match against store name or owner name/email.
- `sort_by`: `created_at` (default), `updated_at`, `id`, or `status`.
- `sort_order`: `asc` or `desc` (default).

Each item includes request status and timestamps, requesting account, store,
current plan, requested plan, billing interval, and the price snapshot saved
with the request. A pending request is explicitly marked
`activation: not_activated`. It is not evidence of payment and does not grant
an entitlement. Payment status is omitted because no authoritative
subscription-payment record exists in the current data model.

Both endpoints use the shared `page` and `per_page` pagination parameters
and response shape documented above. Both require platform-admin
authorization. They are read-only and cannot activate or extend a subscription.


## Feedback support workflow

Feedback support workflow state is independent of email-delivery state. The
existing `status` field continues to describe delivery (`pending`, `sent`,
or `failed`); the separate `support_status` field describes administrative
handling (`new`, `in_progress`, or `resolved`). Changing one never changes
the other. Existing feedback rows are migrated to `new`.

### GET /admin/feedback

Returns a paginated list of feedback records. Optional filters:

- `support_status`: `new`, `in_progress`, or `resolved`.
- `delivery_status`: `pending`, `sent`, or `failed`.
- `category`: `bug`, `suggestion`, `question`, or `other`.
- `search`: case-insensitive match against submission ID, category, message,
  contact name, or contact email.
- `sort_by`: `created_at` (default), `id`, `support_status`, or
  `delivery_status`.
- `sort_order`: `asc` or `desc` (default).

List items include the feedback ID and submission ID, category, optional
contact details, delivery status, support status, creation time, and delivery
time. The full message is returned only by the detail endpoint.

### GET /admin/feedback/{id}

Returns the selected feedback message and the support-handling fields needed
to respond to the submitter. It does not expose SMTP credentials, internal
delivery exception text, session data, or unrelated user/store records.

### PATCH /admin/feedback/{id}/status

Changes the administrative support status. Request:

    {
        "support_status": "in_progress"
    }

Allowed values are `new`, `in_progress`, and `resolved`. An invalid value
returns `400 VALIDATION_ERROR`; a missing feedback record returns
`404 FEEDBACK_NOT_FOUND`.

Every actual status change and its platform audit event are committed in the
same database transaction. The event records the acting administrator,
action `feedback.support_status_changed`, target type
`feedback_submission`, target ID, timestamp, and safe context containing
the submission ID and previous/new support status. Repeating the current
status is idempotent and does not create a duplicate audit event. Email
delivery status and delivery timestamps are not modified.

## Platform audit history

### GET /admin/audit-logs

Returns paginated, read-only platform audit records. Optional filters:

- `actor_user_id`: positive platform administrator user ID.
- `action_type`: exact action name.
- `target_type`: exact target type.
- `target_id`: exact target ID.
- `start_date` and `end_date`: ISO-8601 date or date-time bounds. Date-only
  values cover the full UTC calendar day; date-time values with offsets are
  converted to UTC. The start must be earlier than the end.

The response includes actor ID/name when the actor account still exists,
action, target, safe details, and timestamp. Results are newest first and
use the shared `page` / `per_page` pagination contract. Platform audit
records are separate from store-scoped `/audit` records.

Platform audit rows are append-only. The model rejects ORM update/delete
operations; no API is provided to rewrite or remove audit history.
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

Revokes every active session belonging to the authenticated administrator. It does not accept a target user ID and cannot revoke another administrator's sessions.

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
