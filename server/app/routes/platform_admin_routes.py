from flask import Blueprint

from server.app.middleware.auth_middleware import require_platform_admin
from server.app.services.platform_admin_service import PlatformAdminService


platform_admin_bp = Blueprint("platform_admin", __name__)


@platform_admin_bp.get("/overview")
@require_platform_admin
def overview():
    return PlatformAdminService.overview()


@platform_admin_bp.get("/users")
@require_platform_admin
def list_users():
    return PlatformAdminService.list_users()


@platform_admin_bp.get("/users/<int:user_id>")
@require_platform_admin
def user_detail(user_id):
    return PlatformAdminService.user_detail(user_id)


@platform_admin_bp.get("/stores")
@require_platform_admin
def list_stores():
    return PlatformAdminService.list_stores()


@platform_admin_bp.get("/stores/<int:store_id>")
@require_platform_admin
def store_detail(store_id):
    return PlatformAdminService.store_detail(store_id)
