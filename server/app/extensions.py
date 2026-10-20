# server\app\extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask import request
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

def login_rate_limit_key():
    """Rate-limit an account from a client, not an entire shop LAN."""
    remote_address = get_remote_address()
    payload = request.get_json(silent=True)
    email = payload.get("email", "") if isinstance(payload, dict) else ""
    normalized_email = email.strip().lower() if isinstance(email, str) else ""
    return f"{remote_address}:{normalized_email or 'unknown-account'}"


db = SQLAlchemy(model_class=Base)
limiter = Limiter(key_func=login_rate_limit_key, default_limits=[])