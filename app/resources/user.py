from utils.token_required import token_required
from flask_restful import Resource, reqparse
from bson.objectid import ObjectId
from db import users


class User(Resource):
    # Get user information
    @token_required
    def get(self, user_id):
        # Find the user
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"message": "User not found"}, 404
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
        parser = reqparse.RequestParser()
        parser.add_argument("dob", type=str, help="Date of birth cannot be empty")
        parser.add_argument("weight", type=int)
        parser.add_argument("height", type=int)
        args = parser.parse_args()

        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"message": "User not found"}, 404

        updates = {}

        for key, value in args.items():
            if value:
                updates[key] = value

        users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
        return {"message": "Data updated successfully"}, 200

    # Delete user
    @token_required
    def delete(self, user_id):
        return {"message": "delete user info delete"}
