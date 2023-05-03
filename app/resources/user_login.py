from werkzeug.security import check_password_hash
from flask_restful import Resource, reqparse
from db import users
import jwt
import datetime
from config import SECRET_KEY


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()

        # Check if user exists and passwords match
        user = users.find_one({"email": args["email"]})

        if not user or not check_password_hash(user["password"], args["password"]):
            return {"error": "Invalid username or password"}, 401

        token = jwt.encode(
            {
                "user_id": str(user["_id"]),
                "exp": str(datetime.datetime.utcnow() + datetime.timedelta(minutes=60)),
            },
            SECRET_KEY,
        )
        return {"token": token}, 200
