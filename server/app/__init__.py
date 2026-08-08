# server\app\__init__.py
from flask import Flask
from server.app.extensions import db
from flask_migrate import Migrate
from server.app.routes.auth_routes import auth_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"

# initialize the app with the extension
db.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/auth")

migrate = Migrate(app, db)