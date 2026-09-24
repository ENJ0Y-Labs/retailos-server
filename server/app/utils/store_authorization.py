from flask import session
from server.app.models.store import Store

def get_authorized_store(store_id):
    user_id = session.get("user_id")
    if not user_id or not isinstance(store_id, int):
        return None
    return Store.query.filter_by(id=store_id, user_id=user_id).first()
