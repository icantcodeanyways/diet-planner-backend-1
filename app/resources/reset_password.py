from flask_restful import Resource, reqparse
from db import users
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


class ResetPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email")
        parser.add_argument("password")
        parser.add_argument("reset_code")

        args = parser.parse_args()
        user = users.find_one({"email": args["email"]})

        if not user:
            return {"message": "User not found"}, 404

        if not "password_reset" in user:
            return {"message": "No password reset request found"}, 404

        reset_expiry_time = datetime.fromisoformat(
            str(user["password_reset"]["reset_time"])
        ) + timedelta(minutes=15)
        current_time = datetime.utcnow()

        if current_time > reset_expiry_time:
            users.update_one(
                {"email": user["email"]}, {"$unset": {"password_reset": ""}}
            )
            return {"message": "Reset time expired. Please try again."}, 400

        hashed_password = generate_password_hash(args["password"], method="sha256")
        users.update_one(
            {"email": user["email"]},
            {"$set": {"password": hashed_password}},
            {"$unset": {"password_reset": ""}},
        )
        return {"message": "Password updated successfully"}, 200
