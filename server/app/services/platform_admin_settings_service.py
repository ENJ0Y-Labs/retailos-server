"""Platform-admin self-service profile and session security operations."""

from flask import request, session

from server.app.extensions import db
from server.app.models.platform_audit_log import PlatformAuditLog
from server.app.models.user import PLATFORM_ADMIN_ROLE, User
from server.app.utils.response import Response
from server.app.utils.time import now_utc


class PlatformAdminSettingsService:
    @staticmethod
    def _profile_data(user):
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "platform_role": user.platform_role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    @staticmethod
    def get_profile():
        user = db.session.get(User, session.get("user_id"))
        if not user or user.platform_role != PLATFORM_ADMIN_ROLE:
            return Response.error_response(
                "PLATFORM_ADMIN_REQUIRED",
                "Platform administrator permission is required",
                {},
            ), 403

        return Response.success_response(
            {"user": PlatformAdminSettingsService._profile_data(user)},
            "PLATFORM_ADMIN_PROFILE_RETRIEVED",
        ), 200

    @staticmethod
    def update_profile():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return Response.error_response(
                "VALIDATION_ERROR",
                "A JSON object is required",
                {"payload": "Payload must be a JSON object"},
            ), 400

        unsupported_fields = sorted(set(data) - {"name"})
        if unsupported_fields:
            return Response.error_response(
                "VALIDATION_ERROR",
                "Only the name field can be updated from the administrator profile",
                {field: "This field cannot be changed here" for field in unsupported_fields},
            ), 400

        name = data.get("name")
        if not isinstance(name, str) or len(name.strip()) < 2 or len(name.strip()) > 100:
            return Response.error_response(
                "VALIDATION_ERROR",
                "Name must contain between 2 and 100 characters",
                {"name": "Enter a name between 2 and 100 characters"},
            ), 400

        user = (
            db.session.query(User)
            .filter_by(id=session.get("user_id"))
            .with_for_update()
            .first()
        )
        if not user or user.platform_role != PLATFORM_ADMIN_ROLE:
            return Response.error_response(
                "PLATFORM_ADMIN_REQUIRED",
                "Platform administrator permission is required",
                {},
            ), 403

        normalized_name = name.strip()
        previous_name = user.name
        if previous_name == normalized_name:
            return Response.success_response(
                {
                    "user": PlatformAdminSettingsService._profile_data(user),
                    "changed": False,
                },
                "PLATFORM_ADMIN_PROFILE_UNCHANGED",
            ), 200

        user.name = normalized_name
        db.session.add(PlatformAuditLog(
            actor_user_id=user.id,
            action_type="platform_admin.profile_updated",
            target_type="user",
            target_id=str(user.id),
            details={
                "changed_fields": ["name"],
                "previous": {"name": previous_name},
                "new": {"name": normalized_name},
            },
            created_at=now_utc(),
        ))
        db.session.commit()

        return Response.success_response(
            {
                "user": PlatformAdminSettingsService._profile_data(user),
                "changed": True,
            },
            "PLATFORM_ADMIN_PROFILE_UPDATED",
        ), 200

    @staticmethod
    def revoke_all_sessions():
        user = (
            db.session.query(User)
            .filter_by(id=session.get("user_id"))
            .with_for_update()
            .first()
        )
        if not user or user.platform_role != PLATFORM_ADMIN_ROLE:
            return Response.error_response(
                "PLATFORM_ADMIN_REQUIRED",
                "Platform administrator permission is required",
                {},
            ), 403

        previous_version = user.session_version
        user.session_version += 1
        db.session.add(PlatformAuditLog(
            actor_user_id=user.id,
            action_type="platform_admin.sessions_revoked",
            target_type="user",
            target_id=str(user.id),
            details={
                "scope": "all_sessions",
                "session_version_before": previous_version,
                "session_version_after": user.session_version,
            },
            created_at=now_utc(),
        ))
        db.session.commit()
        session.clear()

        return Response.success_response(
            {"sessions_revoked": "all", "login_required": True},
            "PLATFORM_ADMIN_SESSIONS_REVOKED",
        ), 200
