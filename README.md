# flask_ai_server

- python version : 3.10.14
- tensorflow version : 2.15.0

## 가상환경 설정
1. 파이썬 설치 : `$python3.10 -m venv .venv`
2. 가상환경 만들기 : `$source {PROJECT_PATH}/.venv/bin/activate`
3. tensorflow 설치 : `$pip install tensorflow==2.15.0`
4. pandas 설치 : `$pip install pandas==2.2.2`
5. dotenv 설치 : `$pip install python-dotenv==1.0.1`
6. pytrends 설치 : `$pip install pytrends==4.9.1`
4. 가상환경 종료 시 : `$deactivate`
5. flask 앱 실행 : `$flask run`

## 환경변수

- NAVER_CLIENT_ID : Naver DataLab의 검색어 트랜드 사용 시 네이버 개발자 센터의 Application Client id
- NAVER_CLIENT_SECRET : Naver DataLab의 검색어 트랜드 사용 시 네이버 개발자 센터의 Application Client secret

**환경변수 설정 방법.**
위 가상환경 설정 파트에서 dotenv를 설치하였다면 루트디렉토리에 `.env`라는 이름의 파일 생성 후 아래와 같이 기입.
```text
NAVER_CLIENT_ID=${네이버 클라이언트 아이디}
NAVER_CLIENT_SECRET=${네이버 클라이언트 Secret Key}

```

## API 명세

**1. 매장 모델 혼잡도 반환**
- path : `/model/{매장코드}`
- 매장 코드 : test, gf_factory, pho_ongnam, hello_snack
- request param : `rain_percent`
- example : `http://{SERVER_ADDR}:{PORT}/model/gf_factory?rain_percent={강수량}`
- success response
  ```response
  {
    "data":{
      "congestion":"82"
    }
    ,"isSuccess":true
  }
  ```
- failure response
    ```
  {
    "isSuccess":false
    , "message":"{ERROR_MSG}"}
  }
  ```
