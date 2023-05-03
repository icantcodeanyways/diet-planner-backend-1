from utils.token_required import token_required
from flask_restful import Resource
from bson.objectid import ObjectId
from db import users


class User(Resource):
    # Get user information
    @token_required
    def get(self, user_id):
        # Find the user
        user = users.find_one({"_id": ObjectId(user_id)})
        response = {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "dob": user["dob"],
            "weight": user["weight"],
            "height": user["height"],
            "gender": user["gender"],
        }
        return response

    # Update user info
    @token_required
    def patch(self, user_id):
        return {"message": "update user info put"}

    # Delete user
    @token_required
    def delete(self, user_id):
        return {"message": "delete user info delete"}
