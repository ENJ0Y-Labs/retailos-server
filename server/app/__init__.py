# server/app/__init__.py
from flask import Flask
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate

from server.app.config import Config, ProductionConfig
from server.app.extensions import db
from server.app.routes.alert_routes import alert_bp
from server.app.routes.auth_routes import auth_bp
from server.app.routes.customer_routes import customer_bp
from server.app.routes.dashboard_routes import dashboard_bp
from server.app.routes.product_routes import product_bp
from server.app.routes.sales_routes import sales_bp
from server.app.utils.response import Response


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be configured")

    if config_class is ProductionConfig:
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            raise RuntimeError("DATABASE_URL must be configured in production")

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(product_bp, url_prefix="/product")
    app.register_blueprint(sales_bp, url_prefix="/sales")
    app.register_blueprint(customer_bp, url_prefix="/customers")
    app.register_blueprint(alert_bp, url_prefix="/alerts")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    Migrate(app, db)

    @app.errorhandler(400)
    def bad_request(error):
        return Response.error_response(
            "BAD_REQUEST",
            "The request could not be understood",
            {}
        ), 400

    @app.errorhandler(404)
    def not_found(error):
        return Response.error_response(
            "NOT_FOUND",
            "The requested resource was not found",
            {}
        ), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return Response.error_response(
            "METHOD_NOT_ALLOWED",
            "The requested method is not allowed",
            {}
        ), 405

    @app.errorhandler(IntegrityError)
    def database_conflict(error):
        db.session.rollback()

        return Response.error_response(
            "CONFLICT_ERROR",
            "The request conflicts with existing data",
            {}
        ), 409

    @app.errorhandler(Exception)
    def internal_server_error(error):
        db.session.rollback()
        app.logger.exception("Unhandled server exception")

        return Response.error_response(
            "INTERNAL_SERVER_ERROR",
            "An unexpected server error occurred",
            {}
        ), 500

    return app
