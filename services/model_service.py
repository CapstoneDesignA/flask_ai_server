import numpy as np
import datetime
import logging
import pandas as pd
import tensorflow as tf
from services.data_service import DataService
from utils.dataframe_util import get_max_and_mean_csv, calculate_congestion


class ModelService:
    test_gf_model = tf.keras.models.load_model('./model/test_sales_prediction_model.h5')
    gf_model = tf.keras.models.load_model('./model/model_grandfa_v1.h5')
    pho_model = tf.keras.models.load_model('./model/model_pho_v1.h5')
    hello_model = tf.keras.models.load_model('./model/model_hello_v1.h5')
    target_csv_path_list = ['data/gf_data_test.csv', 'data/final_data_grandfa_factory.csv', 'data/final_data_pho.csv', 'data/final_data_hello.csv']

    @staticmethod
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

    @staticmethod
    def calculate_mean_search_vol_per_time(csv_file_path):
        df = pd.read_csv(csv_file_path)
        recent_df = df.tail(28)
        search_vol_data_per_time = recent_df[['PERIOD', 'SEARCH_VOL']]
        mean_search_vol_per_time = search_vol_data_per_time.groupby('PERIOD')['SEARCH_VOL'].mean()
        return mean_search_vol_per_time

    @staticmethod
    def get_expected_search_vol(target):
        mean_search_vols_per_time = ModelService.calculate_mean_search_vol_per_time(
            ModelService.target_csv_path_list[target])
        if target == 0 or target == 1:
            actual_search_ratio_per_day = DataService.get_trends_by_naver("성수동")
        elif target == 2:
            actual_search_ratio_per_day = DataService.get_trends_by_naver("송정동")
        elif target == 3:
            actual_search_ratio_per_day = DataService.get_trends_by_naver("행운동")
        else:
            raise ValueError("0: test, 1: grandfa_factory, 2 : pho_ongnam, 3 : hello_snack")
        mean_search_ratio = actual_search_ratio_per_day['search_ratio'].mean()
        today_weekday = datetime.datetime.today().weekday()
        mul = actual_search_ratio_per_day.iloc[today_weekday]['search_ratio'] / mean_search_ratio
        ret = mean_search_vols_per_time * mul
        return ret

    @staticmethod
    def predict_congestion(rain_percent, model_type):
        time_info = datetime.datetime.now()
        month = time_info.month
        day = time_info.day
        hour = time_info.hour
        period = ModelService.time_to_period(hour)
        dow = time_info.weekday() + 1
        try :
            expected_search_vol = ModelService.get_expected_search_vol(model_type)  # 0: test, 1: grandfa_factory, 2 : pho, 3 : hello
        except ValueError:
            logging.error("Invalid value for Google Trends search.")
            raise ValueError
        search_volume = expected_search_vol[period]

        new_input = np.array([[month, day, period, rain_percent, dow, search_volume]])
        new_input = new_input.astype('float32')
        if model_type == 0:
            prediction = ModelService.test_gf_model.predict(new_input)
        elif model_type == 1:
            prediction = ModelService.gf_model.predict(new_input)
        elif model_type == 2:
            prediction = ModelService.pho_model.predict(new_input)
        elif model_type == 3:
            prediction = ModelService.hello_model.predict(new_input)
        else:
            raise ValueError("0: test, 1: grandfa_factory, 2 : pho, 3 : hello")

        column_name = 'PAYMENT'
        max_sales, avg_sales = get_max_and_mean_csv(ModelService.target_csv_path_list[model_type], column_name)
        congestion = calculate_congestion(prediction[0], avg_sales, max_sales)
        print("type : " + str(model_type) + ", max_sales : " + str(max_sales) + ", avg_sales : " + str(avg_sales) + ", congestion : " + str(congestion) + ", prediction" + str(prediction))
        ret = str(congestion[0])
        return {'congestion': ret}
