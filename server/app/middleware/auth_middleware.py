from functools import wraps

from flask import session

from server.app.models.user import PLATFORM_ADMIN_ROLE, User
from server.app.utils.response import Response


def require_session(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        session_version = session.get("session_version")
        if not user_id or session_version is None:
            session.clear()
            return Response.error_response(
                "SESSION_NOT_FOUND", "Session not found", {"retryable": False}
            ), 401

        user = User.query.filter_by(id=user_id).first()
        if not user or user.session_version != session_version:
            session.clear()
            return Response.error_response(
                "SESSION_INVALIDATED",
                "Session is no longer valid. Please log in again.",
                {"retryable": False},
            ), 401

        return view_function(*args, **kwargs)

    return wrapper


def require_platform_admin(view_function):
    """Require a valid session and a server-assigned platform-admin role."""
    @wraps(view_function)
    def platform_admin_wrapper(*args, **kwargs):
        user = User.query.filter_by(id=session.get("user_id")).first()
        if not user or user.platform_role != PLATFORM_ADMIN_ROLE:
            return Response.error_response(
                "PLATFORM_ADMIN_REQUIRED",
                "Platform administrator permission is required",
                {},
            ), 403
        return view_function(*args, **kwargs)

    return require_session(platform_admin_wrapper)
