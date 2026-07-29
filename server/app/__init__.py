# server\app\__init__.py
from flask import Flask
from server.app.extensions import db

# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
# initialize the app with the extension
db.init_app(app)