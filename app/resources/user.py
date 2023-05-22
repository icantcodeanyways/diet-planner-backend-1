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
        if len(user["generated_diet_plans"]) == 0:
            consumed_calories = 0
            consumed_fat = 0
            consumed_protien = 0
            consumed_carbs = 0
            breakfast = {
                "consumed_carbs": 0,
                "consumed_fat": 0,
                "consumed_protien": 0,
            }
            dinner = {
                "consumed_carbs": 0,
                "consumed_fat": 0,
                "consumed_protien": 0,
            }
            lunch = {
                "consumed_carbs": 0,
                "consumed_fat": 0,
                "consumed_protien": 0,
            }

        response = {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "activity_factor": user["activity_factor"],
            "dob": user["dob"],
            "weight": user["weight"],
            "height": user["height"],
            "gender": user["gender"],
            "diet_goal": user["diet_goal"],
            "required_calories": user["required_calories"],
            "required_carbs": user["required_carbs"],
            "required_protien": user["required_protien"],
            "required_fat": user["required_fat"],
            "consumed_calories": consumed_calories,
            "consumed_fat": consumed_fat,
            "consumed_carbs": consumed_carbs,
            "consumed_protien": consumed_protien,
            "breakfast_stats": breakfast,
            "lunch_stats": lunch,
            "dinner_stats": dinner,
        }
        return response

    # Update user info
    @token_required
    def patch(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("dob", type=str, help="Date of birth cannot be empty")
        parser.add_argument("weight", type=int)
        parser.add_argument("height", type=int)
        parser.add_argument(
            "activity_factor", type=float, choices=(1, 1.2, 1.4, 1.6, 1.8)
        )
        parser.add_argument("diet_goal", type=str, choices=("gain", "lose", "maintain"))

        args = parser.parse_args()
        print(args)

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
        result = users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 1:
            return {"message": "User deleted successfully"}, 200
        else:
            return {"message": "User not found"}, 404
