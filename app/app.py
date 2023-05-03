from flask import Flask, request
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_restful import Resource, Api
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
        try:
            data = request.get_json()
            email = data["email"]
            first_name = data["first_name"]
            last_name = data["last_name"]
            password = data["password"]
            dob = data["dob"]
            height = float(data["height"])
            weight = float(data["weight"])
            gender = data["gender"]

            # Validate user data
            if not email:
                return {"message": "Email cannot be blank"}, 400
            email = validate_email(email).email
            if not password:
                return {"message": "Password cannot be blank"}, 400
            if not dob:
                return {"message": "Date of birth cannot be blank"}, 400
            if not height:
                return {"message": "Height cannot be blank"}, 400
            if not weight:
                return {"message": "Weight cannot be blank"}, 400
            if not gender:
                return {"message": "Gender cannot be blank"}, 400
            if not first_name or not last_name:
                return {"message": "Name cannot be blank"}, 400
            if not gender in ["male", "female"]:
                return {"message": "Gender has to be either male or female"}, 400
        except KeyError:
            return {"message": "Missing required fileds"}, 400
        except EmailNotValidError:
            return {"message": "Invalid email address"}, 400
        except ValueError:
            return {"message": "Height and weight should be numbers"}, 400

        # Check if user already exist
        if db.users.find_one({"email": email}):
            return {"message" : "User already exists"}, 409

        # Hash password 
        hashed_password = generate_password_hash(password, method="sha256")

        # Insert user into database
        db.users.insert_one(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": hashed_password,
                "dob": dob,
                "weight": weight,
                "height": height,
                "gender": gender,
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
