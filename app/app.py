from flask import Flask
from flask_restful import  Api

from resources.api_status import APIStatus
from resources.user_login import UserLogin
from resources.register_user import UserRegistration
from resources.user import User
from resources.generate_diet_plan import GenerateDietPlan
from resources.diet_plan import DietPlan

app = Flask(__name__)
api = Api(app)

api.add_resource(APIStatus, "/api/status")
api.add_resource(User, "/api/users/<string:user_id>")
api.add_resource(UserRegistration, "/api/users/register")
api.add_resource(UserLogin, "/api/users/login")
api.add_resource(GenerateDietPlan, "/api/users/<string:user_id>/generate_diet_plan")
api.add_resource(DietPlan, "/api/users/<string:user_id>/diet_plans")

# Run the server
if __name__ == "__main__":
    app.run(debug=True)
