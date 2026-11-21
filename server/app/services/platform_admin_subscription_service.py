"""Read-only platform-admin subscription and plan-request queries."""
from datetime import datetime, timedelta, timezone
from flask import g, request
from sqlalchemy import or_
from server.app.extensions import db
from server.app.models.platform_audit_log import PlatformAuditLog
from server.app.models.store import Store
from server.app.models.subscription_change import SubscriptionChange
from server.app.models.user import User
from server.app.services.platform_admin_service import _pagination, _page_args, _subscription
from server.app.services.subscription_service import PLAN_CATALOG
from server.app.utils.response import Response
from server.app.utils.time import now_utc


def _state_filter(query, state, now):
    expired_period = (Store.current_period_end.is_not(None) &
                      (Store.current_period_end <= now))
    if state == "free":
        return query.filter(
            or_(Store.current_plan == "free", Store.current_plan.is_(None)),
            Store.subscription_status != "expired",
        )
    if state == "trial":
        return query.filter(Store.current_plan == "pro",
                            Store.subscription_status == "trial",
                            or_(Store.current_period_end.is_(None), Store.current_period_end > now))
    if state == "active":
        return query.filter(Store.current_plan == "pro",
                            Store.subscription_status == "active",
                            or_(Store.current_period_end.is_(None), Store.current_period_end > now))
    if state == "expired":
        return query.filter(or_(
            Store.subscription_status == "expired",
            (Store.current_plan == "pro") &
            Store.subscription_status.in_(("active", "trial")) & expired_period
        ))
    return query


class PlatformAdminSubscriptionService:
    @staticmethod
    def list_subscriptions():
        page, per_page, error = _page_args()
        if error:
            return error
        now = datetime.now(timezone.utc)
        query = db.session.query(Store).join(User, User.id == Store.user_id)

        state = request.args.get("state")
        if state:
            if state not in ("free", "trial", "active", "expired"):
                return Response.error_response(
                    "VALIDATION_ERROR", "state must be free, trial, active, or expired",
                    {"state": state}
                ), 400
            query = _state_filter(query, state, now)

        plan = request.args.get("plan")
        if plan:
            if plan not in PLAN_CATALOG:
                return Response.error_response("VALIDATION_ERROR", "Unknown plan filter", {"plan": plan}), 400
            query = query.filter(Store.current_plan == plan)

        search = request.args.get("search", "").strip()
        if search:
            pattern = f"%{search}%"
            query = query.filter(or_(Store.name.ilike(pattern), User.name.ilike(pattern), User.email.ilike(pattern)))

        sort_fields = {
            "created_at": Store.created_at, "name": Store.name, "id": Store.id,
            "plan": Store.current_plan, "status": Store.subscription_status,
            "period_end": Store.current_period_end,
        }
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")
        if sort_by not in sort_fields or sort_order not in ("asc", "desc"):
            return Response.error_response(
                "VALIDATION_ERROR", "Unsupported sort_by or sort_order",
                {"sort_by": sort_by, "sort_order": sort_order}
            ), 400
        column = sort_fields[sort_by]
        query = query.order_by(column.asc() if sort_order == "asc" else column.desc(), Store.id.asc())

        def serialize(store):
            owner = db.session.get(User, store.user_id)
            subscription = _subscription(store, now)
            state_value = ("expired" if subscription["subscription_status"] == "expired"
                           else "free" if subscription["plan"] == "free"
                           else subscription["subscription_status"])
            return {
                "store": {"id": store.id, "name": store.name, "created_at": store.created_at.isoformat()},
                "account": {"id": owner.id, "name": owner.name, "email": owner.email} if owner else None,
                "subscription": {**subscription, "state": state_value},
            }

        return Response.success_response(
            _pagination(query, page, per_page, serialize), "PLATFORM_SUBSCRIPTIONS_RETRIEVED"
        ), 200

    @staticmethod
    def list_subscription_requests():
        page, per_page, error = _page_args()
        if error:
            return error
        query = (db.session.query(SubscriptionChange)
                 .join(Store, Store.id == SubscriptionChange.store_id)
                 .join(User, User.id == Store.user_id))

        status = request.args.get("status")
        if status:
            if status not in ("pending", "cancelled"):
                return Response.error_response(
                    "VALIDATION_ERROR", "status must be pending or cancelled", {"status": status}
                ), 400
            query = query.filter(SubscriptionChange.status == status)

        search = request.args.get("search", "").strip()
        if search:
            pattern = f"%{search}%"
            query = query.filter(or_(Store.name.ilike(pattern), User.name.ilike(pattern), User.email.ilike(pattern)))

        sort_fields = {
            "created_at": SubscriptionChange.created_at, "updated_at": SubscriptionChange.updated_at,
            "id": SubscriptionChange.id, "status": SubscriptionChange.status,
        }
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")
        if sort_by not in sort_fields or sort_order not in ("asc", "desc"):
            return Response.error_response(
                "VALIDATION_ERROR", "Unsupported sort_by or sort_order",
                {"sort_by": sort_by, "sort_order": sort_order}
            ), 400
        column = sort_fields[sort_by]
        query = query.order_by(column.asc() if sort_order == "asc" else column.desc(),
                               SubscriptionChange.id.asc())
        now = datetime.now(timezone.utc)

        def serialize(change):
            store = db.session.get(Store, change.store_id)
            owner = db.session.get(User, store.user_id) if store else None
            current = _subscription(store, now) if store else None
            requested_plan = PLAN_CATALOG.get(change.target_plan, PLAN_CATALOG["free"])
            return {
                "id": change.id,
                "status": change.status,
                "requested_at": change.created_at.isoformat(),
                "updated_at": change.updated_at.isoformat(),
                "requested_by": change.requested_by,
                "account": {"id": owner.id, "name": owner.name, "email": owner.email} if owner else None,
                "store": {"id": store.id, "name": store.name} if store else None,
                "current_plan": {
                    "id": current["plan"], "name": current["plan_name"],
                    "subscription_status": current["subscription_status"],
                } if current else None,
                "requested_plan": {
                    "id": change.target_plan, "name": requested_plan["name"],
                    "billing_interval": change.billing_interval,
                    "price": {"amount": change.price_amount, "currency": "NGN"},
                },
                "activation": "not_activated" if change.status == "pending" else "not_granted_by_request",
            }

        return Response.success_response(
            _pagination(query, page, per_page, serialize), "PLATFORM_SUBSCRIPTION_REQUESTS_RETRIEVED"
        ), 200


    @staticmethod
    def grant_premium(store_id):
        """Grant a time-limited Pro entitlement after an operator verifies payment."""
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not {"duration_days", "reason"}.issubset(data) or set(data) - {
            "duration_days", "reason", "payment_reference"
        }:
            return Response.error_response(
                "VALIDATION_ERROR",
                "Provide duration_days and reason, with optional payment_reference",
                {},
            ), 400

        duration_days = data.get("duration_days")
        if isinstance(duration_days, bool) or not isinstance(duration_days, int) or not 1 <= duration_days <= 3650:
            return Response.error_response(
                "VALIDATION_ERROR", "duration_days must be an integer between 1 and 3650", {}
            ), 400

        reason = data.get("reason")
        if not isinstance(reason, str) or len(reason.strip()) < 8 or len(reason.strip()) > 500:
            return Response.error_response(
                "VALIDATION_ERROR", "reason must contain between 8 and 500 characters", {}
            ), 400

        payment_reference = data.get("payment_reference")
        if payment_reference is not None and (
            not isinstance(payment_reference, str) or len(payment_reference.strip()) > 120
        ):
            return Response.error_response(
                "VALIDATION_ERROR", "payment_reference must be 120 characters or fewer", {}
            ), 400

        store = db.session.get(Store, store_id)
        if not store:
            return Response.error_response("STORE_NOT_FOUND", "Store not found", {}), 404
        owner = db.session.get(User, store.user_id)
        now = datetime.now(timezone.utc)
        current_end = store.current_period_end
        if current_end is not None:
            if current_end.tzinfo is None:
                current_end = current_end.replace(tzinfo=timezone.utc)
            else:
                current_end = current_end.astimezone(timezone.utc)

        # Preserve any remaining active Pro/trial time instead of shortening it.
        starts_at = max(now, current_end) if (
            store.current_plan == "pro"
            and store.subscription_status in ("active", "trial")
            and current_end is not None
        ) else now
        ends_at = starts_at + timedelta(days=duration_days)

        previous = {
            "plan": store.current_plan,
            "subscription_status": store.subscription_status,
            "current_period_end": store.current_period_end.isoformat() if store.current_period_end else None,
        }
        store.current_plan = "pro"
        store.subscription_status = "active"
        store.current_period_end = ends_at

        db.session.add(PlatformAuditLog(
            actor_user_id=g.platform_admin.id,
            action_type="subscription.premium_granted",
            target_type="store",
            target_id=str(store.id),
            details={
                "owner_user_id": owner.id if owner else None,
                "previous": previous,
                "new_plan": "pro",
                "duration_days": duration_days,
                "starts_at": starts_at.isoformat(),
                "ends_at": ends_at.isoformat(),
                "verification_channel": "manual_whatsapp_bank_transfer",
                "payment_reference": payment_reference.strip() if payment_reference else None,
                "reason": reason.strip(),
            },
            created_at=now_utc(),
        ))
        db.session.commit()

        return Response.success_response({
            "store": {"id": store.id, "name": store.name, "owner_user_id": store.user_id},
            "subscription": {
                "plan": store.current_plan,
                "subscription_status": store.subscription_status,
                "current_period_start": starts_at.isoformat(),
                "current_period_end": ends_at.isoformat(),
                "duration_days": duration_days,
            },
        }, "PREMIUM_ENTITLEMENT_GRANTED"), 200
