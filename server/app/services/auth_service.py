# server\app\services\auth_service.py
from flask import session, request
from server.app.models.user import User
from server.app.utils.response import Response
from server.app.utils.security import hash_password, verify_password
from server.app.extensions import db
class AuthService:
    def __init__(self):
        pass
    
    def register_user(self):
        
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # validate input
        if username.isalnum() and password.isalnum() and len(password) >= 6 and '@' in email and '.' in email:
                
            # check if email exists
            user = User.query.filter_by(email = email).first()
            if user is None:
                # hash password
                hashed = hash_password(password)
                
                # create user
                user = User(
                    name = username,
                    email = email,
                    password_hash = hashed
                )
                
                db.session.add(user)
                db.session.flush()
                db.session.commit()
                
                print(user.id)
                
                # return structured response
                data = f'''
                    {{
                        "user": {{
                            "id": {user.id} ,
                            "username": {user.name},
                            "email": {user.email},
                            "created_at": {user.created_at}
                        }}
                    }}
                '''
                message = "REGISTARATION_SUCCESSFUL"
                return Response.success_response(data, message)
            else:
                code = "EMAIL_ALREADY_EXISTS"
                message = "Email already exists"
                
                return Response.error_response(code, message)
        else:
            code= "VALIDATION_ERROR"
            message = "Invalid input data"
            fields = '''
                {{
                    "name" : "Username must be alphanumeric",
                    "email" : "Invalid email format",
                    "password" : "Password must be at least 6 characters long and alphanumeric",
                }}
            '''

            return Response.error_response(code, message, fields)
        
    def login_user(self):
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # verify email + password
        if '@' in email and  '.' in email and len(password) >= 6 and password.isalnum():
            
            # find user by email
            user = User.query.filter_by(email=email).first()
            
            if user is not None:
                
                # check password
                verified = verify_password(password, user.password_hash)
                
                if verified:
                    # set session
                    session["user_id"] = user.id

                    data = f'''
                        {{
                            "user": {{
                                "id": {user.id} ,
                                "username": {user.name},
                                "email": {user.email},
                                "created_at": {user.created_at}
                            }}
                        }}
                    '''
                    message = "LOGIN_SUCCESSFUL"
                    
                    return Response.success_response(data, message)
                else:
                    code = "AUTH_INVALID_CREDENTIALS"
                    message = "Invalid email or password"
                    field = '''
                        {
                            "password" : "Invalid password"
                        }
                    '''
                    return Response.error_response(code, message, field)
            else:
                code = "AUTH_INVALID_CREDENTIALS"
                message = "Invalid email or password"
                field = '''
                    {
                        "email" : "Email not found"
                    }
                '''
                return Response.error_response(code, message, field)
        else:
            code = "VALIDATION_ERROR"
            message = "Invalid input data"
            fields = '''
                {{
                    "email" : "Invalid email format",
                    "password" : "Password must be at least 6 characters long and alphanumeric",
                }}
            '''
            return Response.error_response(code, message, fields)
    
    def logout_user(self):
        user_id = session.get('user_id')
        
        user = User.query.filter_by(id = user_id).first()
        
        if user is not None:
            session.pop("user_id", None)
            
            data = f'''
                {{
                    "user": {{
                        "id": {user.id} ,
                        "username": {user.name},
                        "email": {user.email},
                        "created_at": {user.created_at}
                    }}
                }}
            '''
            message = "LOGOUT_SUCCESSFUL"
            return Response.success_response(data, message)
        
        else:
            code = "USER_NOT_FOUND"
            message = "User not found"
            fields = '''
                {
                    "user_id" : "User with the given ID does not exist"
                }
            '''
            
            return Response.error_response(code, message, fields)