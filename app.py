import numpy as np
import pandas as pd
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


def calculate_congestion(prediction, average_sales, max_sales, average_congestion=40):
    if prediction <= 0:
        return 0
    elif prediction == average_sales:
        return average_congestion
    else:
        if prediction >= max_sales:
            return 100
        else:
            return average_congestion + ((prediction - average_sales)
                                         / (max_sales - average_sales)) * (100 - average_congestion)


def get_max_and_mean_csv(csv_file_path, column_name):
    df = pd.read_csv(csv_file_path)

    if column_name not in df.columns:
        raise ValueError("Non Existent Column")
    max_value = df[column_name].max()
    average_value = df[column_name].mean()

    return max_value, average_value

@app.route('/test')
def index():
    return 'test'


@app.route('/test/model')
def restful_model_predict_test():
    parameter_dict = request.args.to_dict()
    required_params = ['rain_percent']
    for param in required_params:
        if param not in parameter_dict:
            return toFailureResponse('rain_percent param is necessary.'), 400

    try:
        rain_percent = float(parameter_dict['rain_percent'])
    except ValueError as e:
        return toFailureResponse('rain_percent is not numeric.'), 400

    time_info = datetime.datetime.now()
    month = time_info.month
    day = time_info.day
    hour = time_info.hour
    dow = time_info.weekday() + 1

    search_volume = 100  # todo : 검색량은 Flask Server에서 계산하여 넣기.
    new_input = np.array([[month, day, dow, hour, rain_percent, search_volume]])
    new_input = new_input.astype('float32')
    prediction = test_model.predict(new_input)

    path = 'data/gf_data_test.csv'
    column_name = 'PAYMENT'
    max_sales, avg_sales = get_max_and_mean_csv(path, column_name)
    congestion = calculate_congestion(prediction, avg_sales, max_sales)
    ret = str(congestion)
    data = {'congestion': ret}
    res = toSuccessResponse(data)
    return res, 200


if __name__ == '__main__':
    app.run(debug=True)
