# server\app\config.py
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///store.db'
    TESTING = False

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
