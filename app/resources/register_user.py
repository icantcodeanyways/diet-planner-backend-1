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
            }
        )

        return {"message": "User registered successfully."}, 201
