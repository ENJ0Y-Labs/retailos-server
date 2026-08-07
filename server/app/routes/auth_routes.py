# server\app\routes\auth_routes.py
from flask import Blueprint
from server.app.services.auth_service import AuthService
from server.app.middleware.auth_middleware import  require_session

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods = ["POST"])
def register():
    return AuthService.register_user()

@auth_bp.route("/login", methods = ["POST"])
def login():
    return AuthService.login_user()

@auth_bp.route("/logout", methods = ["POST"])
@require_session
def logout():
    return AuthService.logout_user()