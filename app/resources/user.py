from utils.token_required import token_required
from flask_restful import Resource, reqparse
from bson.objectid import ObjectId
from datetime import datetime
from db import users


class User(Resource):
    # Get user information
    @token_required
    def get(self, user_id):
        # Find the user
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"message": "User not found"}, 404
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

        if len(user["generated_diet_plans"]) != 0:
            today = datetime.now().strftime("%d/%m/%Y")
            for diet_plans in user["generated_diet_plans"]:
                if today in diet_plans:
                    todays_plans = diet_plans[str(today)]

            for plan in todays_plans:
                consumed_calories += plan["total_calories"]
                consumed_fat += plan["total_fat"]
                consumed_protien += plan["total_protien"]
                consumed_carbs += plan["total_carbs"]

                if plan["meal_timing"] == "breakfast":
                    breakfast["consumed_fat"] = plan["total_fat"]
                    breakfast["consumed_protien"] = plan["total_protien"]
                    breakfast["consumed_protien"] = plan["total_protien"]
                elif plan["meal_timing"] == "lunch":
                    lunch["consumed_fat"] = plan["total_fat"]
                    lunch["consumed_protien"] = plan["total_protien"]
                    lunch["consumed_protien"] = plan["total_protien"]
                elif plan["meal_timing"] == "dinner":
                    dinner["consumed_fat"] = plan["total_fat"]
                    dinner["consumed_protien"] = plan["total_protien"]
                    dinner["consumed_protien"] = plan["total_protien"]

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
