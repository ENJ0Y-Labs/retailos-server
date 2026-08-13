# server\app\__init__.py
from flask import Flask
from server.app.extensions import db
from flask_migrate import Migrate
from server.app.routes.auth_routes import auth_bp

def create_app(config_class): 
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # initialize the app with the extension
    db.init_app(app)
    app.secret_key = '854c17e3094dc13670c236a3a3a7daf0397f89d43cf0d7942a1754ba1b3ae667'
    app.register_blueprint(
        auth_bp, 
        url_prefix="/auth"
    )
    
    Migrate(app, db)
    
    return app