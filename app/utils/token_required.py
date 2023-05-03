import datetime
import jwt
from flask import request  
from functools import wraps
from config import SECRET_KEY

# Decorater function to protect routes
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return {"message": "Token is missing"}, 401

        try:
            # Verify the token using the secret key
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data["user_id"]
        except:
            return ({"message": "Token is invalid"}), 401

        # Add the user ID to the request parameters
        kwargs["user_id"] = user_id
        return func(*args, **kwargs)

    return decorated
