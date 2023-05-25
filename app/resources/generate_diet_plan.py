from sys import exception
from pulp import LpMinimize, LpProblem, LpVariable, LpMaximize, lpSum, LpStatus
from utils.token_required import token_required
from flask_restful import Resource, request
import requests
from bson.objectid import ObjectId
import random
from db import users
from config import FOOD_DATABASE_API_ENDPOINT
from config import APP_ID
from config import APP_KEY


class GenerateDietPlan(Resource):
    # Generate diet plan
    @token_required
    def post(self, user_id):
        try:
            selected_meals = request.get_json()["selected_meals"]
            if len(selected_meals) < 3:
                return {"message": "Please select three or more meals please."}, 400
            if len(selected_meals) != len(set(selected_meals)):
                return {"message": "Duplicate entries not allowed."}, 400

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
                        "ingr": selected_meals[i],
                    },
                ).json()

                if (
                    len(response["parsed"]) == 0
                    or selected_meals[i].strip().lower()
                    != response["parsed"][0]["food"]["label"].strip().lower()
                ):
                    hints = response["hints"]
                    if len(hints) == 0:
                        return {
                            "message": "Diet plan cannot be generated due to missing meal info"
                        }, 400
                    for hint in hints:
                        if (
                            hint["food"]["label"].strip().lower()
                            == selected_meals[i].strip().lower()
                        ):
                            response["parsed"] = [hint]
                            break
                    if len(response["parsed"]) == 0:
                        response["parsed"] = response["hints"]

                meal_info = {}
                meal_info["meal_item"] = selected_meals[i]
                try:
                    meal_info["calories"] = (
                        float(response["parsed"][0]["food"]["nutrients"]["ENERC_KCAL"])
                        / 100
                    )
                except KeyError:
                    return {
                        "message : Diet plan cannot be generated with the given food items. Please choose some other food items."
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

                meal_list.append(meal_info)

            diet_plan = []
            food_vars = [meal["meal_item"] for meal in meal_list]
            food_calories = [meal["calories"] for meal in meal_list]
            food_protein = [meal["protien"] for meal in meal_list]
            food_fat = [meal["fat"] for meal in meal_list]
            food_carbs = [meal["carbs"] for meal in meal_list]

            # Please work, please
            prob = LpProblem("Maximize_Calories", LpMaximize)
            food_amounts = LpVariable.dicts(
                "Food_Amount", food_vars, lowBound=0, cat="Continuous"
            )

            prob += lpSum(
                [
                    food_amounts[food_vars[i]] * food_calories[i]
                    for i in range(len(food_vars))
                ]
            )
            print(prob)

            prob += lpSum(
                [
                    food_amounts[food_vars[i]] * food_protein[i]
                    for i in range(len(food_vars))
                ]
            ) <= (user["required_protien"] / 3)

            prob += lpSum(
                [
                    food_amounts[food_vars[i]] * food_protein[i]
                    for i in range(len(food_vars))
                ]
            ) >= ((user["required_protien"] / 3) - 50)
            prob += lpSum(
                [
                    food_amounts[food_vars[i]] * food_fat[i]
                    for i in range(len(food_vars))
                ]
            ) <= (user["required_fat"] / 3)
            prob += lpSum(
                [
                    food_amounts[food_vars[i]] * food_fat[i]
                    for i in range(len(food_vars))
                ]
            ) >= ((user["required_fat"] / 3) - 50)
            prob += lpSum(
                [
                    food_amounts[food_vars[i]] * food_carbs[i]
                    for i in range(len(food_vars))
                ]
            ) <= (user["required_carbs"] / 3)
            prob += lpSum(
                [
                    food_amounts[food_vars[i]] * food_carbs[i]
                    for i in range(len(food_vars))
                ]
            ) >= ((user["required_carbs"] / 3) - 50)

            prob.solve()
            """ print(food_amounts) """
            """ print("Status:", LpStatus[prob.status]) """
            """ print(type(food_amounts)) """

            for food in food_vars:
                amount = food_amounts[food].varValue
                print(food, amount)

            # I hope that has worked..

            for meal in meal_list:
                diet = {}
                diet["calories"] = meal["calories"]
                diet["item"] = meal["meal_item"]
                diet["protien"] = meal["protien"]
                diet["fat"] = meal["fat"]
                diet["carbs"] = meal["carbs"]
                diet["quantity"] = food_amounts[meal["meal_item"]].varValue
                diet["image"] = meal["image"]
                diet_plan.append(diet)

            return diet_plan

        except KeyError as error:
            print(f"Something fucked up here {error}")
            return {"message": "Invalid request"}, 400
