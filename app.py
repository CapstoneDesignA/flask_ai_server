import numpy as np
import tensorflow as tf
import datetime

from flask import Flask, request
from flask_restful import Api, Resource
from tensorflow import keras

app = Flask(__name__)
api = Api(app)

test_model = tf.keras.models.load_model('./model/test_sales_prediction_model.h5')


def toFailureResponse(msg):
    response = {'isSuccess': False, 'message': msg}
    return response

def toSuccessResponse(data):
    response = {'isSuccess': True, 'data': data}
    return response
@app.route('/test')
def index():
    return 'test'

@app.route('/test/model')
def restful_model_predict_test():
    parameter_dict = request.args.to_dict()
    required_params = ['rain_percent', 'search_volume']
    for param in required_params:
        if param not in parameter_dict:
            return toFailureResponse('rain_percent, search_volume param is necessary.'), 400

    try:
        rain_percent = float(parameter_dict['rain_percent'])
        search_volume = float(parameter_dict['search_volume'])
    except ValueError as e:
        return toFailureResponse('rain_percent, search_volume is not numeric.'), 400

    time_info = datetime.datetime.now()
    month = time_info.month
    day = time_info.day
    hour = time_info.hour
    dow = time_info.weekday() + 1

    new_input = np.array([[month, day, dow, hour, rain_percent, search_volume]])
    new_input = new_input.astype('float32')
    prediction = test_model.predict(new_input)
    ret = str(prediction[0][0])

    data = {'congestion': ret}
    res = toSuccessResponse(data)
    return res, 200

if __name__ == '__main__':
    app.run(debug=True)
