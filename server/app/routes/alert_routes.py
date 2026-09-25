from flask import Blueprint
from server.app.middleware.auth_middleware import require_session
from server.app.services.alert_service import AlertService

alerts = AlertService()
alert_bp = Blueprint("alerts", __name__)


@alert_bp.route("", methods=["GET"])
@require_session
def list_alerts():
    return alerts.list_alerts()


@alert_bp.route("/generate-low-stock", methods=["POST"])
@require_session
def generate_low_stock():
    return alerts.generate_low_stock_alerts()


@alert_bp.route("/resolve", methods=["POST"])
@require_session
def resolve_alert():
    return alerts.resolve_alert()
