from flask_restful import Resource

class MainRoutes(Resource):
    def get(self):
        return 'test'
