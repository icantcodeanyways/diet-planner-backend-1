from utils.token_required import token_required
from flask_restful import Resource

class User(Resource):
    # Get user information
    @token_required
    def get(self, user_id):
        return {"message": "get user info get"}

    # Update user info
    @token_required
    def patch(self, user_id):
        return {"message": "update user info put"}

    # Delete user
    @token_required
    def delete(self, user_id):
        return {"message": "delete user info delete"}
