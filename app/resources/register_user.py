from datetime import datetime
from flask_restful import Resource, reqparse
from db import users
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash


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
        parser.add_argument(
            "activity_factor", type=int, choices=(1, 1.2, 1.4, 1.6, 1.8), required=True
        )
        args = parser.parse_args()
        try:
            args["email"] = validate_email(args["email"]).email
        except EmailNotValidError:
            return {"message": "Invalid email address"}, 400

        # Check if user already exist
        if users.find_one({"email": args["email"]}):
            return {"message": "User already exists"}, 409

        # Hash password
        hashed_password = generate_password_hash(args["password"], method="sha256")

        # Calculate age
        age = datetime.now().year - int(args["dob"].split("/")[2])
        if age <= 0:
            return {"message": "Invalid date of birth"}, 400

        # Calculate required calories
        required_calories = 0
        if args["gender"] == "male":
            required_calories = (
                655.1
                + ((9.563 * args["weight"]) + (1.850 * args["height"]) - (4.676 * age))
            ) * args["activity_factor"]
        elif args["gender"] == "female":
            required_calories = (
                66.47
                + ((13.75 * args["weight"]) + (5.003 * args["height"]) - (6.755 * age))
                * args["activity_factor"]
            )

        # Insert user into database
        users.insert_one(
            {
                "first_name": args["first_name"],
                "last_name": args["last_name"],
                "email": args["email"],
                "password": hashed_password,
                "dob": args["dob"],
                "weight": args["weight"],
                "height": args["height"],
                "gender": args["gender"],
                "activity_factor": args["activity_factor"],
                "required_calories": required_calories,
                "generated_diet_plans": [],
            }
        )

        return {"message": "User registered successfully."}, 201
