# TX RetailOS subscription plans

## Published catalog

The server's `PLAN_CATALOG` in `server/app/services/subscription_service.py` is the authoritative source for plan prices, entitlements, and limits. Do not duplicate prices or limits as server-side constants elsewhere.

| Plan | Price | Products | Customers | Sales per Africa/Lagos calendar month |
|---|---:|---:|---:|---:|
| Free | ₦0/month | 100 | 100 | 500 |
| Pro | ₦4,999/month | Unlimited | Unlimited | Unlimited |

Both plans include inventory, sales/checkout, and the current dashboard. Pro's advanced-reporting entitlement is catalog metadata; a future advanced-reporting feature must enforce that entitlement server-side before it is exposed.

## Endpoints

- `GET /subscriptions/plans`: public plan catalog, including price, limits, and feature entitlements.
- `GET /subscriptions?store_id=1`: authenticated current plan, status, billing period end, and pending plan change. Store ownership is checked on the server.
- `POST /subscriptions/change`: authenticated request to change plans. JSON fields: `store_id` and `plan` (`free` or `pro`).
- `POST /subscriptions/change/cancel`: authenticated cancellation of a pending request. JSON fields: `store_id` and `change_id`.

## Billing safety

A plan-change request is recorded as pending. The current plan and entitlements do not change because the client asked for an upgrade. The response explicitly reports that billing is not configured and that activation has not occurred.

Paid plan activation is intentionally unavailable until a payment provider integration is implemented with verified server-side payment confirmation, idempotent event handling, and consistent handling of pending, failed, and successful payments. Never add a public endpoint that accepts a client-supplied `success` flag or directly sets a store to Pro.

## Enforcement

The server checks the current plan before creating a product, customer, or sale. The Free plan is limited to 100 currently stored products, 100 currently stored customers, and 500 sales created during the current Africa/Lagos calendar month. Pro has no cap for those resources. These checks are server-side and do not rely on the frontend.

## Remaining launch requirement

Configure and test a real billing provider before advertising paid upgrades as purchasable. The current implementation safely records requests but cannot collect or verify payments, renew subscriptions, or transition a paid subscription after verified payment.