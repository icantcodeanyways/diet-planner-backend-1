from utils.token_required import token_required
from flask_restful import Resource


class GenerateDietPlan(Resource):
    # Generate diet plan
    @token_required
    def post(self):
        return {"message": "generate diet plan"}
