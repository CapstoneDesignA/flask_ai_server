# flask_ai_server

- python version : 3.10.14
- tensorflow version : 2.15.0

## 가상환경 설정
1. 파이썬 설치 : `$python3.10 -m venv .venv`
2. 가상환경 만들기 : `$source {PROJECT_PATH}/.venv/bin/activate`
3. tensorflow 설치 : `$pip install tensorflow==2.15.0`
4. 가상환경 종료 시 : `$deactivate`
5. flask 앱 실행 : `$flask run`

## API 명세

**1. 테스트 모델 혼잡도 반환**
- path : `/test/model`
- request param : `rain_percent`, `search_volume`
- example : `http://{SERVER_ADDR}:{PORT}/test/model?rain_percent={강수량}&search_volume={검색량}`
- success response
  ```response
  {
    "data":{
      "congestion":"168.44548"
    }
    ,"isSuccess":true
  }
  ```
- failure response
    ```
  {
    "isSuccess":false
    , "message":"{ERROR_MSG}"}
  ```
  