import numpy as np
import pandas as pd
import tensorflow as tf
import datetime
import urllib.request
import json
import os

from flask import Flask, request
from flask_restful import Api, Resource
from pytrends.request import TrendReq

app = Flask(__name__)
api = Api(app)

target_csv_path_list = ['data/gf_data_test.csv']
client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')

test_model = tf.keras.models.load_model('./model/test_sales_prediction_model.h5')
pytrends = TrendReq(hl='ko', tz=540)



def to_failure_response(msg):
    response = {'isSuccess': False, 'message': msg}
    return response


def to_success_response(data):
    response = {'isSuccess': True, 'data': data}
    return response


# Google trends를 통하여 최근 일주일 상대 검색량 반환. -> pytrends오류로 인한 개발 중지.
def get_grandfa_factory_trends_google():
    # https://trends.google.co.kr/trends/explore?date=today%201-m&geo=KR&q=%2Fm%2F043rlyx&hl=ko
    try:
        pytrends.build_payload(["성수동2가"], cat=0, timeframe='now 7-d', geo='KR', gprop='')
    except ValueError as ve:
        print("구글 트렌드에 검색하기 위한 Value가 잘못되었습니다.")
    except Exception as e:
        print("구글 트렌드에서 검색결과를 가져올 수 없습니다.")
    data = pytrends.interest_over_time()


# 네이버 데이터랩을 통하여 최근 7일에 대한 상대 검색량을 반환. MON to SUN 순으로 되어있음.
def get_grandfa_factory_trends_naver():
    url = "https://openapi.naver.com/v1/datalab/search";
    today = datetime.datetime.now()
    end_date = today - datetime.timedelta(days=1)
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date = today - datetime.timedelta(days=7)
    start_date_str = start_date.strftime('%Y-%m-%d')
    body = f"""{{
        "startDate": "{start_date_str}",
        "endDate": "{end_date_str}",
        "timeUnit": "date",
        "keywordGroups": [
            {{
                "groupName": "성수동",
                "keywords" : ["성수동"]
            }}
        ],
        "device": "mo"
    }}"""
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
    else:
        print("Error Code:" + rescode)
        return
    parsed_json = json.loads(response_body)
    data_items = parsed_json['results'][0]['data']
    df = pd.DataFrame(data_items)
    df.columns = ['date', 'search_ratio']
    df['date'] = pd.to_datetime(df['date'])
    df['weekday'] = df['date'].dt.strftime('%a').str.upper()
    weekday_mapping = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}
    df['weekday_num'] = df['weekday'].map(weekday_mapping)
    df = df.sort_values('weekday_num').reset_index(drop=True)
    df = df[['weekday', 'search_ratio']]
    return df


# prediction : 매출, average_sales : 평균 매출, max_sales : 최대 매출, average_congestion : 평균 혼잡도(0~100)
# 혼잡도를 반환함
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


# 데이터 내의 컬럼의 max_value와 mean_value를 구함.
def get_max_and_mean_csv(csv_file_path, column_name):
    df = pd.read_csv(csv_file_path)

    if column_name not in df.columns:
        raise ValueError("Non Existent Column")
    max_value = df[column_name].max()
    average_value = df[column_name].mean()

    return max_value, average_value


# 최근 28일 데이터를 통하여 각 시간대별 평균 검색량은 반환.
def calculate_mean_search_vol_per_time(csv_file_path):
    df = pd.read_csv(csv_file_path)
    recent_df = df.tail(28)
    search_vol_data_per_time = recent_df[['TIME', 'SEARCH_VOL']]
    mean_search_vol_per_time = search_vol_data_per_time.groupby('TIME')['SEARCH_VOL'].mean()

    return mean_search_vol_per_time


# 파라미터로 가게에 대해 정해놓은 인덱스 값을 넣어 시간대별로 기대되는 검색량을 반환함.
def get_expected_search_vol(target):
    mean_search_vols_per_time = calculate_mean_search_vol_per_time(target_csv_path_list[target])
    if target == 1:
        actual_search_ratio_per_day = get_grandfa_factory_trends_naver()
    else:
        raise ValueError("0 : grandfa_factory")
    mean_search_ratio = actual_search_ratio_per_day['search_ratio'].mean()
    today_weekday = datetime.datetime.today().weekday()
    mul = actual_search_ratio_per_day.iloc[today_weekday]['search_ratio'] / mean_search_ratio
    ret = mean_search_vols_per_time * mul

    return ret


# 시간을 구간별로 나누어 1부터 6사이의 정수로 치환
def time_to_period(hour):
    if 0 <= hour < 6:
        return 1
    elif 6 <= hour < 11:
        return 2
    elif 11 <= hour < 14:
        return 3
    elif 14 <= hour < 17:
        return 4
    elif 17 <= hour < 21:
        return 5
    elif 21 <= hour < 24:
        return 6
    else:
        raise ValueError("Hour must be between 0 and 23")


@app.route('/test')
def index():
    return 'test'


@app.route('/test/model')
def restful_model_predict_test():
    parameter_dict = request.args.to_dict()
    required_params = ['rain_percent']
    for param in required_params:
        if param not in parameter_dict:
            return to_failure_response('rain_percent param is necessary.'), 400

    try:
        rain_percent = float(parameter_dict['rain_percent'])
    except ValueError as e:
        return to_failure_response('rain_percent is not numeric.'), 400

    # Model 에 입력할 파라미터 준비
    time_info = datetime.datetime.now()
    month = time_info.month
    day = time_info.day
    hour = time_info.hour
    period = time_to_period(hour)
    dow = time_info.weekday() + 1
    expected_search_vol = get_expected_search_vol(0) # 0 : 할아버지 공장
    search_volume = expected_search_vol[period]

    new_input = np.array([[month, day, dow, period, rain_percent, search_volume]])
    new_input = new_input.astype('float32')
    prediction = test_model.predict(new_input)

    column_name = 'PAYMENT'
    max_sales, avg_sales = get_max_and_mean_csv(target_csv_path_list[0], column_name)
    congestion = calculate_congestion(prediction[0], avg_sales, max_sales)
    ret = str(congestion[0])
    data = {'congestion': ret}
    res = to_success_response(data)
    return res, 200


if __name__ == '__main__':
    app.run(debug=True)
