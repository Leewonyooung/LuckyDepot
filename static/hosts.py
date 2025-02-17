import os
from dotenv import load_dotenv
import firebase_admin, json
from firebase_admin import credentials, auth



firebase_auth = auth

load_dotenv(override=True)
LUCKYDEPOT_SDK = os.getenv("LUCKYDEPOT_SDK")
POSTGRESQL_HOST = os.getenv('POSTGRESQL_HOST')
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
EXCEPT_PATH_LIST = [
    "/openapi.json", 
]

firebase_key_json = os.getenv("LUCKYDEPOT_SDK")
if not firebase_key_json:
    cred = credentials.Certificate("lucky-depot-firebase-adminsdk-fbsvc-f5947922f7.json")
else:
    firebase_key = json.loads(firebase_key_json)
    cred = credentials.Certificate(firebase_key)
    print(cred)

# cred = credentials.Certificate("lucky-depot-firebase-adminsdk-fbsvc-f5947922f7.json")  # 서비스 계정 키 경로
firebase_admin.initialize_app(cred)

EXCEPT_PATH_REGEX = r"^(/.*|/docs|/redoc|/auth|/order/.*|/hub/.*|/driver/.*|/deliver/.*|/category/.*|/ml.*|/login/.*|)$"
TRUSTED_HOSTS = ["*"]
ALLOW_SITE = ["*"]
