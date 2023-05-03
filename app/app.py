from flask import Flask, request
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_restful import Resource, Api, reqparse
from pymongo import MongoClient
from config import MONGO_URI

app = Flask(__name__)
api = Api(app)
app.config["MONGO_URI"] = MONGO_URI
client = MongoClient(MONGO_URI)
db = client["dietplannerDB"]


class APIStatus(Resource):
    def get(self):
        return {"status": "ok"}


class UserLogin(Resource):
    def post(self):
        return {"message": "user login post"}


class UserRegistration(Resource):
    def post(self):
        # Validate user data
        parser = reqparse.RequestParser()
        parser.add_argument(
            "email", type=str, help="Email cannot be empty", required=True
        )
        parser.add_argument(
            "first_name", type=str, help="First name cannot be empty", required=True
        )
        parser.add_argument(
            "last_name", type=str, help="Last name cannot be empty", required=True
        )
        parser.add_argument(
            "password", type=str, help="Password cannot be empty", required=True
        )
        parser.add_argument(
            "dob", type=str, help="Date of birth cannot be empty", required=True
        )
        parser.add_argument("weight", type=int, required=True)
        parser.add_argument("height", type=int, required=True)
        parser.add_argument(
            "gender",
            type=str,
            choices=("male", "female"),
            required=True,
        )
        args = parser.parse_args()
        try:
            args["email"] = validate_email(args["email"]).email
        except EmailNotValidError:
            return {"message": "Invalid email address"}, 400

        # Check if user already exist
        if db.users.find_one({"email": args["email"]}):
            return {"message": "User already exists"}, 409

        # Hash password
        hashed_password = generate_password_hash(args["password"], method="sha256")

        # Insert user into database
        db.users.insert_one(
            {
                "first_name": args["first_name"],
                "last_name": args["last_name"],
                "email": args["email"],
                "password": hashed_password,
                "dob": args["dob"],
                "weight": args["weight"],
                "height": args["height"],
                "gender": args["gender"],
            }
        )

        return {"message": "User registered successfully."}, 201


class User(Resource):
    # Get user information
    def get(self, user_id):
        return {"message": "get user info get"}

    # Update user info
    def patch(self, user_id):
        return {"message": "update user info put"}

    # Delete user
    def delete(self, user_id):
        return {"message": "delete user info delete"}


class GenerateDietPlan(Resource):
    # Generate diet plan
    def post(self):
        return {"message": "generate diet plan"}


class DietPlan(Resource):
    # Return geenrated diet plans
    def get(self):
        return {"message": "Generated diet plans"}


api.add_resource(APIStatus, "/api/status")
api.add_resource(User, "/api/users/<string:user_id>")
api.add_resource(UserRegistration, "/api/users/register")
api.add_resource(UserLogin, "/api/users/login")
api.add_resource(GenerateDietPlan, "/api/users/<string:user_id>/generate_diet_plan")
api.add_resource(DietPlan, "/api/users/<string:user_id>/diet_plans")

# Run the server
if __name__ == "__main__":
    app.run(debug=True)
