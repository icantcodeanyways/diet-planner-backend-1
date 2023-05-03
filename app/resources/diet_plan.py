from flask_restful import Resource
from utils.token_required import token_required

class DietPlan(Resource):
    # Return geenrated diet plans
    @token_required
    def get(self):
        return {"message": "Generated diet plans"}


