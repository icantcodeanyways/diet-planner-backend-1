import datetime
import jwt
from flask import request
from functools import wraps
from config import SECRET_KEY
import time


# Decorater function to protect routes
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return {"message": "Please login to view the page"}, 401

        try:
            # Verify the token using the secret key
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data["user_id"]

            # Check if token has expired or not
            if data["exp"] < time.time():
                return {"message": "Session expired. Please login again."}, 401
        except:
            return ({"message": "Invalid token. Please login again."}), 401

        # Add the user ID to the request parameters
        kwargs["user_id"] = user_id
        return func(*args, **kwargs)

    return decorated
