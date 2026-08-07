# server\app\routes\auth_routes.py
from flask import Blueprint
from server.app.services.auth_service import AuthService
from server.app.middleware.auth_middleware import  require_session

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", method = ["POST"])
def register():
    return AuthService.register_user()

@auth_bp.route("/login", method = ["POST"])
def login():
    return AuthService.login_user()

@auth_bp.route("/logout", method = ["POST"])
def logout():
    return AuthService.logout_user()