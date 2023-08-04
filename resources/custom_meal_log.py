from utils.token_required import token_required
from flask_restful import Resource, request
import requests
from bson.objectid import ObjectId
from db import users
from config import FOOD_DATABASE_API_ENDPOINT
from config import APP_ID
from config import APP_KEY
from datetime import datetime
from flask_restful import reqparse


class CustomMeal(Resource):
    # Generate diet plan
    @token_required
    def post(self, user_id):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument(
                "meal_timing",
                type=str,
                choices=("breakfast", "lunch", "dinner"),
                required=True,
            )
            parser.add_argument(
                "meal_name",
                type=str,
                required=True,
            )
            parser.add_argument(
                "total_calories",
                type=float,
                required=True,
            )
            parser.add_argument(
                "total_fat",
                type=float,
                required=True,
            )
            parser.add_argument(
                "total_carbs",
                type=float,
                required=True,
            )
            parser.add_argument(
                "total_protien",
                type=float,
                required=True,
            )
            parser.add_argument(
                "quantity",
                type=float,
                required=True,
            )
            args = parser.parse_args()
            print(args)
            meal_name = args["meal_name"]
            total_calories = args["total_calories"]
            total_carbs = args["total_carbs"]
            total_fat = args["total_fat"]
            total_protien = args["total_protien"]
            quantity = args["quantity"]

            user = users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {"message": "User not found"}, 404

            meal_timing = args["meal_timing"]

            today = datetime.now().strftime("%d/%m/%Y")
            todays_diet_plans = None
            if len(user["generated_diet_plans"]) != 0:
                for diet_plans in user["generated_diet_plans"]:
                    if today in diet_plans:
                        todays_diet_plans = diet_plans[str(today)]

                if todays_diet_plans:
                    if len(todays_diet_plans) == 3:
                        print("here")
                        return {"message": "Diet plans already exist"}, 409

                    for diet_plan in todays_diet_plans:
                        if diet_plan["meal_timing"] == meal_timing:
                            print("yeah here")
                            print(diet_plan["meal_timing"], meal_timing)
                            return {"message": "Diet plan already exist"}, 409

            diet_plan = {
                "diet_plan": [
                    {
                        "item": meal_name,
                        "quantity": quantity,
                        "image": "https://i.imgur.com/MEupGps.png",
                        "calories" : total_calories,
                        "protien" : total_protien,
                        "fat" : total_fat,
                        "carbs" : total_carbs,
                    }
                ]
            }

            diet_plan["total_calories"] = total_calories
            diet_plan["total_fat"] = total_fat
            diet_plan["total_protien"] = total_protien
            diet_plan["total_carbs"] = total_carbs
            diet_plan["meal_timing"] = meal_timing

            if todays_diet_plans:
                query = {
                    "_id": ObjectId(user_id),
                    "generated_diet_plans": {"$elemMatch": {today: {"$exists": True}}},
                }
                """ document = users.find_one(query) """
                users.update_one(
                    query,
                    {"$push": {f"generated_diet_plans.$.{today}": diet_plan}},
                )

            else:
                users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$push": {"generated_diet_plans": {today: [diet_plan]}}},
                )

            return {"message": "Custom meal logged successfully"}, 200

        except KeyError as error:
            print(f"Something messed up here {error}")
            return {"message": "Invalid request"}, 400
