from flask_restful import Resource

class APIStatus(Resource):
    def get(self):
        return {"status": "ok"}


