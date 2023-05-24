from flask_restful import Resource
from utils.token_required import token_required
from db import users
from bson.objectid import ObjectId
from flask import request
from datetime import datetime


class DietPlan(Resource):
    # Return geenrated diet plans
    @token_required
    def get(self, user_id):
        # Find the user
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"message": "User not found"}, 404
        generated_diet_plans = user["generated_diet_plans"]
        if len(generated_diet_plans) == 0:
            return {"message": "You have no generated meal plans"}, 404
        return generated_diet_plans, 200

    @token_required
    def post(self, user_id):
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"message": "User not found"}, 404

        diet_plan = request.get_json()
        meals = request.get_json()["diet_plan"]
        meal_timing = request.get_json()["diet_timing"]

        today = datetime.now().strftime("%d/%m/%Y")

        todays_diet_plans = None
        if len(user["generated_diet_plans"]) != 0:
            for diet_plans in user["generated_diet_plans"]:
                if today in diet_plans:
                    todays_diet_plans = diet_plans[str(today)]

            if todays_diet_plans:
                if len(todays_diet_plans) == 3:
                    return {"message": "Diet plans already exist"}, 409

                for diet_plan in todays_diet_plans:
                    if diet_plan["meal_timing"] == meal_timing:
                        return {"message": "Diet plan already exist"}, 409

        total_calories = 0
        total_carbs = 0
        total_fat = 0
        total_protien = 0

        for meal in meals:
            total_calories += meal["calories"] * meal["quantity"]
            total_carbs += meal["carbs"] * meal["quantity"]
            total_fat += meal["fat"] * meal["quantity"]
            total_protien += meal["protien"] * meal["quantity"]

        diet_plan["total_calories"] = total_calories
        diet_plan["total_fat"] = total_fat
        diet_plan["total_protien"] = total_protien
        diet_plan["total_carbs"] = total_carbs

        if todays_diet_plans:
            query = {
                "_id": ObjectId(user_id),
                "generated_diet_plans": {"$elemMatch": {today: {"$exists": True}}},
            }
            document = users.find_one(query)
            users.update_one(
                query,
                {"$push": {f"generated_diet_plans.$.{today}": diet_plan}},
            )

        else:
            users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"generated_diet_plans": {today: [diet_plan]}}},
            )

        return {"message": "okda"}, 200
