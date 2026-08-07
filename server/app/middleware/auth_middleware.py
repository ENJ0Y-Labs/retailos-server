# server\app\middleware\auth_middleware.py
from functools import wraps
from flask import session
from server.app.utils.response import Response

def require_session(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        
        # 1. Check if user identifier exists in cookie-backed session
        if not user_id:
            
            # 2. Block and reject API request
            code = "SESSION_NOT_FOUND"
            message = "Session not found"
            fields = []
            return Response.error_response(code, message, fields)
        
        # 3. Pass to route if session is active
        return view_function(*args, **kwargs)
    return wrapper
 