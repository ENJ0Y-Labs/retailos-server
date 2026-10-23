"""Server-authoritative subscription plans and entitlement checks.

Prices and limits live in PLAN_CATALOG. Paid plan activation is deliberately
not performed by a client request; it requires a verified billing integration.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import request
from server.app.extensions import db
from server.app.models.customer import Customer
from server.app.models.product import Product
from server.app.models.sale import Sale
from server.app.models.store import Store
from server.app.models.subscription_change import SubscriptionChange
from server.app.utils.response import Response
from server.app.utils.store_authorization import get_authorized_store


PLAN_CATALOG = {
    "free": {
        "id": "free",
        "name": "Free",
        "price": {"amount": 0, "currency": "NGN", "interval": "month"},
        "limits": {"products": 100, "customers": 100, "sales_per_month": 500},
        "features": {
            "inventory": True,
            "sales_and_checkout": True,
            "dashboard": True,
            "advanced_reporting": False,
        },
    },
    "pro": {
        "id": "pro",
        "name": "Pro",
        "price": {"amount": 4999, "currency": "NGN", "interval": "month"},
        "limits": {"products": None, "customers": None, "sales_per_month": None},
        "features": {
            "inventory": True,
            "sales_and_checkout": True,
            "dashboard": True,
            "advanced_reporting": True,
        },
    },
}


def current_period_start(now=None):
    """Return the UTC instant at the start of the current Africa/Lagos month."""
    now = now or datetime.now(timezone.utc)
    local_now = now.astimezone(ZoneInfo("Africa/Lagos"))
    local_start = local_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return local_start.astimezone(timezone.utc)


class SubscriptionService:
    @staticmethod
    def _store_data(store):
        plan = PLAN_CATALOG.get(store.current_plan, PLAN_CATALOG["free"])
        return {
            "store_id": store.id,
            "plan": plan,
            "subscription_status": store.subscription_status,
            "current_period_end": (
                store.current_period_end.isoformat()
                if store.current_period_end else None
            ),
        }

    def list_plans(self):
        return Response.success_response(
            {"plans": list(PLAN_CATALOG.values())},
            "SUBSCRIPTION_PLANS_RETRIEVED",
        ), 200

    def current_subscription(self):
        store_id = request.args.get("store_id", type=int)
        store = get_authorized_store(store_id)
        if not store:
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {},
            ), 403

        pending = SubscriptionChange.query.filter_by(
            store_id=store.id, status="pending"
        ).order_by(SubscriptionChange.created_at.desc()).first()
        data = self._store_data(store)
        data["pending_change"] = ({
            "id": pending.id,
            "target_plan": pending.target_plan,
            "status": pending.status,
            "created_at": pending.created_at.isoformat(),
            "payment_required": pending.target_plan != "free",
        } if pending else None)
        return Response.success_response(
            {"subscription": data}, "SUBSCRIPTION_RETRIEVED"
        ), 200

    def request_change(self):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return Response.error_response(
                "VALIDATION_ERROR", "Payload must be a JSON object", {}
            ), 400

        store_id = data.get("store_id")
        target_plan = data.get("plan")
        store = get_authorized_store(store_id)
        if not store:
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {},
            ), 403
        if target_plan not in PLAN_CATALOG:
            return Response.error_response(
                "INVALID_PLAN", "Select a plan from the published plan catalog",
                {"plan": "Unknown plan"},
            ), 400
        if target_plan == store.current_plan:
            return Response.error_response(
                "PLAN_ALREADY_ACTIVE", "This plan is already active", {}
            ), 409

        existing = SubscriptionChange.query.filter_by(
            store_id=store.id, status="pending"
        ).first()
        if existing:
            if existing.target_plan == target_plan:
                return Response.success_response(
                    {
                        "change": {
                            "id": existing.id,
                            "target_plan": existing.target_plan,
                            "status": existing.status,
                            "payment_required": target_plan != "free",
                            "activation": "not_activated",
                        }
                    },
                    "PLAN_CHANGE_ALREADY_PENDING",
                ), 200
            return Response.error_response(
                "PLAN_CHANGE_PENDING",
                "Resolve the existing pending plan change before requesting another",
                {"pending_change_id": existing.id},
            ), 409

        change = SubscriptionChange(
            store_id=store.id,
            requested_by=store.user_id,
            source_plan=store.current_plan,
            target_plan=target_plan,
            status="pending",
        )
        db.session.add(change)
        db.session.commit()

        # Never grant paid access based on a client claim. A verified payment
        # provider integration must confirm the payment before changing Store.
        return Response.success_response(
            {
                "change": {
                    "id": change.id,
                    "source_plan": change.source_plan,
                    "target_plan": change.target_plan,
                    "status": change.status,
                    "price": PLAN_CATALOG[target_plan]["price"],
                    "payment_required": PLAN_CATALOG[target_plan]["price"]["amount"] > 0,
                    "activation": "not_activated",
                },
                "billing": {
                    "status": "not_configured",
                    "message": "Paid plan activation requires verified billing confirmation.",
                },
            },
            "PLAN_CHANGE_PENDING",
        ), 202

    def cancel_pending_change(self):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return Response.error_response(
                "VALIDATION_ERROR", "Payload must be a JSON object", {}
            ), 400
        store_id = data.get("store_id")
        change_id = data.get("change_id")
        store = get_authorized_store(store_id)
        if not store:
            return Response.error_response(
                "STORE_ACCESS_DENIED",
                "You do not have access to this store",
                {},
            ), 403
        change = SubscriptionChange.query.filter_by(
            id=change_id, store_id=store.id, status="pending"
        ).first()
        if not change:
            return Response.error_response(
                "PENDING_CHANGE_NOT_FOUND",
                "No matching pending plan change was found",
                {},
            ), 404
        change.status = "cancelled"
        change.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return Response.success_response(
            {"change_id": change.id, "status": change.status},
            "PLAN_CHANGE_CANCELLED",
        ), 200

    @staticmethod
    def check_limit(store_id, resource):
        """Return a standard API error tuple when a Free-plan limit is reached."""
        store = db.session.get(Store, store_id)
        if not store:
            return None
        plan = PLAN_CATALOG.get(store.current_plan, PLAN_CATALOG["free"])
        limit = plan["limits"].get(resource)
        if limit is None:
            return None

        if resource == "products":
            count = Product.query.filter_by(store_id=store_id).count()
        elif resource == "customers":
            count = Customer.query.filter_by(store_id=store_id).count()
        elif resource == "sales_per_month":
            start = current_period_start()
            count = Sale.query.filter(
                Sale.store_id == store_id,
                Sale.created_at >= start,
            ).count()
        else:
            return None

        if count < limit:
            return None
        return Response.error_response(
            "PLAN_LIMIT_REACHED",
            f"The {plan['name']} plan limit for {resource} has been reached",
            {
                "resource": resource,
                "limit": limit,
                "current": count,
                "current_plan": plan["id"],
                "upgrade_available": plan["id"] != "pro",
            },
        ), 403
