from flask_restful import Resource, reqparse
import datetime
import random
from flask_mail import Mail, Message
from db import users


class ForgotPassword(Resource):
    def __init__(self, app):
        self.app = app
        self.mail = Mail(app)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True)
        args = parser.parse_args()
        user = users.find_one({"email": args["email"]})

        if not user:
            return {"message": "No user exist with that email"}, 404

        code = str(random.randint(100000, 999999))

        with self.app.app_context():
            message = Message(
                "Diet planner app password reset code", recipients=[args["email"]]
            )
            message.body = (
                "Your password reset code for diet planner application is: {}".format(
                    code
                )
            )
            try:
                self.mail.send(message)
                users.update_one(
                    {"_id": user["_id"]},
                    {
                        "$set": {
                            "password_reset": {
                                "reset_code": code,
                                "reset_time": datetime.datetime.utcnow(),
                            }
                        }
                    },
                )
                return {"message": "Password reset code send successfully"}, 200
            except Exception as e:
                print(e)
                return {
                    "message": "Could not send password reset code. Please try again later."
                }, 500
