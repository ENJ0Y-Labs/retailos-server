# server\app\utils\response.py
def success_response(data=None, message=""):
    return {
        "success": True,
        "data": data,
        "message": message
    }

def error_response(code, message, fields=None):
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "fields": fields or {}
        }
    }