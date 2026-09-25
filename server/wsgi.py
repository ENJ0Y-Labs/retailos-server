# server/wsgi.py
from server.app import create_app
from server.app.config import ProductionConfig


application = create_app(ProductionConfig)
