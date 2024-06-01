import os

class Config:
    CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
    CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

    if not CLIENT_ID or not CLIENT_SECRET:
        raise EnvironmentError("NAVER_CLIENT_ID or NAVER_CLIENT_SECRET environment variables not set.")
