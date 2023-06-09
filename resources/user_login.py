from werkzeug.security import check_password_hash
from flask_restful import Resource, reqparse
from db import users
import jwt
import datetime
from config import SECRET_KEY


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "email", type=str, help="Email cannot be empty", required=True
        )
        parser.add_argument(
            "password", type=str, help="Password cannot be empty", required=True
        )
        args = parser.parse_args()

        # Check if user exists and passwords match
        user = users.find_one({"email": args["email"]})

        if not user or not check_password_hash(user["password"], args["password"]):
            return {"message": "Invalid username or password"}, 401

        # Expiration time for the token
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        token = jwt.encode(
            {"user_id": str(user["_id"]), "exp": expires_at},
            SECRET_KEY,
            algorithm="HS256",
        )
        return {"token": token}, 200
