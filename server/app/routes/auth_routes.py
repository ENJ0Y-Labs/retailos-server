from flask import Blueprint
from server.app.services.auth_service import AuthService
from server.app.middleware.auth_middleware import require_session
from server.app.extensions import limiter

auth = AuthService()
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    return auth.register_user()

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    return auth.login_user()

@auth_bp.route("/me", methods=["GET"])
@require_session
def me():
    return auth.current_user()

@auth_bp.route("/logout", methods=["POST"])
@require_session
def logout():
    return auth.logout_user()
