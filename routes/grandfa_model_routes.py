from flask import request
from flask_restful import Resource
from services.model_service import ModelService
from utils.response_util import to_failure_response, to_success_response

class GrandfaModelRoutes(Resource):
    def get(self):
        parameter_dict = request.args.to_dict()
        required_params = ['rain_percent']
        for param in required_params:
            if param not in parameter_dict:
                return to_failure_response('rain_percent param is necessary.'), 400

        try:
            rain_percent = float(parameter_dict['rain_percent'])
        except ValueError:
            return to_failure_response('rain_percent is not numeric.'), 400

        try:
            result = ModelService.predict_congestion(rain_percent, 1)
            return to_success_response(result), 200
        except Exception as e:
            return to_failure_response("Internal Server Error."), 500
