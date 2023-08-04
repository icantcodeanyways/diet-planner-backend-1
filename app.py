from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from resources.api_status import APIStatus
from resources.user_login import UserLogin
from resources.register_user import UserRegistration
from resources.user import User
from resources.generate_diet_plan import GenerateDietPlan
from resources.diet_plan import DietPlan
from resources.forgot_password import ForgotPassword
from resources.reset_password import ResetPassword
from resources.custom_food_log import CustomFoodLog
from resources.custom_meal_log import CustomMeal

app = Flask(__name__)

# Cors allow all origin (to be changed later)
CORS(app)

api = Api(app)

# App configs (to be refactored into separate file later)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "charname40@gmail.com"
app.config["MAIL_PASSWORD"] = "etiojkfcdctjazrd"
app.config["MAIL_DEFAULT_SENDER"] = "charname40@gmail.com"

api.add_resource(APIStatus, "/api/status")
api.add_resource(User, "/api/users/<string:user_id>")
api.add_resource(UserRegistration, "/api/users/register")
api.add_resource(UserLogin, "/api/users/login")
api.add_resource(GenerateDietPlan, "/api/users/<string:user_id>/generate_diet_plan")
api.add_resource(DietPlan, "/api/users/<string:user_id>/diet_plans")
api.add_resource(
    ForgotPassword, "/api/users/forgot_password", resource_class_kwargs={"app": app}
)
api.add_resource(ResetPassword, "/api/users/reset_password")
api.add_resource(CustomFoodLog, "/api/users/<string:user_id>/custom_food_log")
api.add_resource(CustomMeal, "/api/users/<string:user_id>/custom_meal_log")

# Run the server
if __name__ == "__main__":
    app.run(debug=True)
