# server\app\services\auth_service.py
from sqlite3 import IntegrityError

from flask import session, request
from server.app.models.user import User
from server.app.utils.response import Response
from server.app.utils.security import hash_password, verify_password
from server.app.extensions import db
class AuthService:
    def __init__(self):
        pass
    
    def register_user(self):
        try:
            # extract input
            data = request.get_json(silent=False)

            if not isinstance(data, dict):
                code = "VALIDATION_ERROR"
                message = "invalid input data"
                fields = {
                    "payload" : "Payload must be a JSON object"
                }
                return Response.error_response(code, message, fields), 400

            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not isinstance(username, str) or not isinstance(email, str) or not isinstance(password, str):
                code = "VALIDATION_ERROR"
                message = "Invalid input data"
                fields = {
                    "name": "Username must be a string",
                    "email": "Email must be a string",
                    "password": "Password must be a string"
                }
                return Response.error_response(code, message, fields), 400

            # validate input
            if username.isalnum():
                if password.isalnum():
                    if len(password) >= 6:
                        if '@' in email and '.' in email:
                            user = User.query.filter_by(email=email).first()
                            if user is None:
                                hashed = hash_password(password)
                                user = User(
                                    name=username,
                                    email=email,
                                    password_hash=hashed
                                    )
                                db.session.add(user)
                                db.session.flush()
                                db.session.commit()

                                # return structured response
                                data = {
                                    "user": {
                                        "id": user.id,
                                        "username": user.name,
                                        "email": user.email,
                                        "created_at": user.created_at.isoformat()
                                    }
                                }
                                message = "REGISTRATION_SUCCESSFUL"
                                return Response.success_response(data, message), 200
                            else:
                                code = "EMAIL_ALREADY_EXISTS"
                                message = "Email already exists"
                                fields = {"email": "Email is already registered"}
                                return Response.error_response(code, message, fields), 400
                        else:
                            code = "VALIDATION_ERROR"
                            message = "Invalid email format"
                            fields = {"email": "Invalid email format"}

                            return Response.error_response(code, message, fields), 400
                    else:
                        code = "VALIDATION_ERROR"
                        message = "Password must be at least 6 characters long"
                        fields = {"password": "Password must be at least 6 characters long"}

                        return Response.error_response(code, message, fields), 400
                else:
                    code = "VALIDATION_ERROR"
                    message = "Password must be alphanumeric"
                    fields = {"password": "Password must be alphanumeric"}

                    return Response.error_response(code, message, fields), 400
            else:
                code = "VALIDATION_ERROR"
                message = "Username must be alphanumeric"
                fields = {"username": "Username must be alphanumeric"}

                return Response.error_response(code, message, fields), 400
        except IntegrityError:
            return Response.error_response(
                code="CONFLICT_ERROR",
                message="Database constraint violation",
                fields={
                    "email": "Unable to login due to database constraint"
                }
            ), 409

        except Exception as e:
            return Response.error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                fields={
                    "error": str(e)
                }
            ), 500


    def login_user(self):
        try:
            data = request.get_json(silent=False)

            if not isinstance(data, dict):
                code = "VALIDATION_ERROR"
                message = "invalid input data"
                fields = {
                    "payload" : "Payload must be a JSON object"
                }
                return Response.error_response(code, message, fields), 400
        
            email = data.get('email')
            password = data.get('password')

            if not isinstance(email, str) or not isinstance(password, str):
                code = "VALIDATION_ERROR"
                message = "Invalid input data"
                fields = {"password": "Password must be a string"}
                return Response.error_response(code, message, fields), 400

            # verify email + password
            if '@' in email and '.' in email and len(password) >= 6 and password.isalnum():
                
                # find user by email
                user = User.query.filter_by(email=email).first()

                if user is not None:
                    
                    # check password
                    verified = verify_password(password, user.password_hash)
                    if verified:
                        
                        # set session
                        session["user_id"] = user.id
                        
                        data = {
                            "user": {
                                "id": user.id,
                                "username": user.name,
                                "email": user.email,
                                "created_at": user.created_at.isoformat()
                            }
                        }
                        message = "LOGIN_SUCCESSFUL"
                        
                        return Response.success_response(data, message), 200
                    else:
                        code = "AUTH_INVALID_CREDENTIALS"
                        message = "Invalid email or password"
                        field = {"password": "Invalid password"}
                        return Response.error_response(code, message, field), 401
                else:
                    code = "AUTH_INVALID_CREDENTIALS"
                    message = "Invalid email or password"
                    field = {"email": "Email not found"}
                    return Response.error_response(code, message, field), 401
            else:
                code = "VALIDATION_ERROR"
                message = "Invalid input data"
                fields = {
                    "email": "Invalid email format",
                    "password": "Password must be at least 6 characters long and alphanumeric"
                }
                return Response.error_response(code, message, fields), 400
        except IntegrityError:
            return Response.error_response(
                code="CONFLICT_ERROR",
                message="Database constraint violation",
                fields={
                    "email": "Unable to login due to database constraint"
                }
            ), 409

        except Exception as e:
            return Response.error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                fields={
                    "error": str(e)
                }
            ), 500


    def logout_user(self):
        user_id = session.get('user_id')
        
        user = User.query.filter_by(id=user_id).first()
        
        if user is not None:
            session.pop("user_id", None)
            
            data = {
                "user": {
                    "id": user.id,
                    "username": user.name,
                    "email": user.email,
                    "created_at": user.created_at.isoformat()
                }
            }
            message = "LOGOUT_SUCCESSFUL"
            return Response.success_response(data, message), 200
        else:
            code = "USER_NOT_FOUND"
            message = "User not found"
            fields = {"user_id": "User with the given ID does not exist"}
            return Response.error_response(code, message, fields), 401