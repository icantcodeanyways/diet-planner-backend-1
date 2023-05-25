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


class CustomFoodLog(Resource):
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
            parser.add_argument("log_info", type=list, required=True, location="json")
            args = parser.parse_args()
            selected_meals = args["log_info"]

            if len(selected_meals) == 0:
                return {"message": "Meals cannot be null"}, 400

            for meal in selected_meals:
                try:
                    if not meal["food"] or not meal["quantity"]:
                        return {
                            "message": "Invalid request. Please provided proper data"
                        }, 400
                except TypeError:
                    return {
                        "message": "Invalid request. Please provided proper data"
                    }, 400

            user = users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {"message": "User not found"}, 404

            meal_list = []
            for i in range(len(selected_meals)):
                response = requests.get(
                    FOOD_DATABASE_API_ENDPOINT,
                    params={
                        "app_key": APP_KEY,
                        "app_id": APP_ID,
                        "ingr": selected_meals[i]["food"],
                    },
                ).json()

                if len(response["parsed"]) == 0:
                    if len(response["hints"]) != 0:
                        response["parsed"] = response["hints"]
                    else:
                        break
                meal_info = {}
                meal_info["item"] = selected_meals[i]["food"]
                try:
                    meal_info["calories"] = (
                        float(response["parsed"][0]["food"]["nutrients"]["ENERC_KCAL"])
                        / 100
                    )
                except KeyError:
                    return {
                        "message : Unable to log diet plan due to missing data."
                    }, 400
                try:
                    meal_info["protien"] = (
                        float(response["parsed"][0]["food"]["nutrients"]["PROCNT"])
                        / 100
                    )
                except KeyError as error:
                    meal_info["protien"] = 0

                try:
                    meal_info["fat"] = (
                        float(response["parsed"][0]["food"]["nutrients"]["FAT"]) / 100
                    )
                except KeyError as error:
                    meal_info["fat"] = 0

                try:
                    meal_info["carbs"] = (
                        float(response["parsed"][0]["food"]["nutrients"]["CHOCDF"])
                        / 100
                    )
                except KeyError as error:
                    meal_info["carbs"] = 0

                try:
                    meal_info["image"] = response["parsed"][0]["food"]["image"]
                except KeyError as error:
                    meal_info["image"] = "https://i.imgur.com/MEupGps.png"

                """ print(selected_meals[i]) """
                meal_info["quantity"] = float(selected_meals[i]["quantity"])
                meal_list.append(meal_info)
            print(meal_list)

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

            total_calories = 0
            total_carbs = 0
            total_fat = 0
            total_protien = 0

            for meal in meal_list:
                total_calories += meal["calories"] * meal["quantity"]
                total_carbs += meal["carbs"] * meal["quantity"]
                total_fat += meal["fat"] * meal["quantity"]
                total_protien += meal["protien"] * meal["quantity"]

            diet_plan = {
                "diet_plan": meal_list,
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

            return {"message": "Custom diet plan added successfully"}, 200

        except KeyError as error:
            print(f"Something messed up here {error}")
            return {"message": "Invalid request"}, 400
