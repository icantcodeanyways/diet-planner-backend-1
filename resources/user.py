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
            todays_plans = None
            for diet_plans in user["generated_diet_plans"]:
                if today in diet_plans:
                    todays_plans = diet_plans[str(today)]

            if todays_plans:
                for plan in todays_plans:
                    consumed_calories += plan["total_calories"]
                    consumed_fat += plan["total_fat"]
                    consumed_protien += plan["total_protien"]
                    consumed_carbs += plan["total_carbs"]

                    if plan["meal_timing"] == "breakfast":
                        breakfast["consumed_fat"] = plan["total_fat"]
                        breakfast["consumed_protien"] = plan["total_protien"]
                        breakfast["consumed_carbs"] = plan["total_carbs"]
                    elif plan["meal_timing"] == "lunch":
                        lunch["consumed_fat"] = plan["total_fat"]
                        lunch["consumed_protien"] = plan["total_protien"]
                        lunch["consumed_carbs"] = plan["total_carbs"]
                    elif plan["meal_timing"] == "dinner":
                        dinner["consumed_fat"] = plan["total_fat"]
                        dinner["consumed_protien"] = plan["total_protien"]
                        dinner["consumed_carbs"] = plan["total_carbs"]

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

        # Recalculate stuff
        age = datetime.now().year - int(user["dob"].split("/")[2])

        # Calculate required calories
        required_calories = 0
        if user["gender"] == "male":
            required_calories = (
                655.1
                + ((9.563 * args["weight"]) + (1.850 * args["height"]) - (4.676 * age))
            ) * args["activity_factor"]
        elif user["gender"] == "female":
            required_calories = (
                66.47
                + ((13.75 * args["weight"]) + (5.003 * args["height"]) - (6.755 * age))
                * args["activity_factor"]
            )

        # Calculate required carbs
        required_carbs = 0
        if args["diet_goal"] == "gain":
            required_carbs = 0.65 * required_calories
        elif args["diet_goal"] == "maintain":
            required_carbs = 0.50 * required_calories
        elif args["diet_goal"] == "maintain":
            required_carbs = 0.45 * required_calories

        required_carbs = required_carbs / 4

        # Calculate required protien
        required_protien = 0
        if args["diet_goal"] == "gain":
            required_protien = 2 * args["weight"]
        elif args["diet_goal"] == "maintain":
            required_protien = 1.3 * args["weight"]
        elif args["diet_goal"] == "maintain":
            required_protien = 1.6 * args["weight"]

        # Calculate required fat
        required_fat = 0
        if args["diet_goal"] == "gain":
            required_fat = 0.35 * required_calories
        elif args["diet_goal"] == "maintain":
            required_fat = 0.25 * required_calories
        elif args["diet_goal"] == "maintain":
            required_fat = 0.20 * required_calories

        required_fat = required_fat / 4

        updates = {}

        for key, value in args.items():
            if value:
                updates[key] = value

        updates["required_calories"] = required_calories
        updates["required_fat"] = required_fat
        updates["required_carbs"] = required_carbs
        updates["required_protien"] = required_protien

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
