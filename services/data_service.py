import datetime
import urllib.request
import json
import pandas as pd
import logging
from config import Config
from pytrends.request import TrendReq

class DataService:

    pytrends = TrendReq(hl='ko', tz=540)

    @staticmethod
    def get_trends_by_naver(keyword):
        url = "https://openapi.naver.com/v1/datalab/search"
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
                    "groupName": "{keyword}",
                    "keywords": ["{keyword}"]
                }}
            ],
            "device": "mo"
        }}"""
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", Config.CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", Config.CLIENT_SECRET)
        request.add_header("Content-Type", "application/json")
        response = urllib.request.urlopen(request, data=body.encode("utf-8"))
        rescode = response.getcode()
        if rescode == 200:
            response_body = response.read()
        else:
            raise Exception(f"Error Code: {rescode}")
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

    @staticmethod
    def get_grandfa_factory_trends_google():
        try:
            DataService.pytrends.build_payload(["성수동2가"], cat=0, timeframe='now 7-d', geo='KR', gprop='')
            data = DataService.pytrends.interest_over_time()
        except ValueError:
            logging.error("Invalid value for Google Trends search.")
        except Exception as e:
            logging.error(f"Could not fetch Google Trends data: {e}")
