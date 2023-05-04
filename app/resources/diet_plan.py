from flask_restful import Resource
from utils.token_required import token_required
from db import users
from bson.objectid import ObjectId

class DietPlan(Resource):
    # Return geenrated diet plans
    @token_required
    def get(self, user_id):
        # Find the user
        user = users.find_one({"_id" : ObjectId(user_id)})
        if not user:
            return {"message" : "User not found"}, 404
        generated_diet_plans = user["generated_diet_plans"]
        if len(generated_diet_plans) == 0:
            return {"message" : "You have no generated meal plans"}, 404
        return generated_diet_plans, 200
