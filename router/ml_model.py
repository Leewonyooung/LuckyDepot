from fastapi import APIRouter, Depends
# from pydantic import BaseModel
from joblib import load
# from datetime import datetime, date
import router.deliver as deliver
from database.conn.connection import db
from sqlalchemy.orm import Session
from sortedcollections import NearestDict

router = APIRouter()

# 머신러닝 모델 로드
model = load('./machine_learning/model/cluster_ny_gb.joblib')
# Feature: [['Ship Mode', 'year', 'month', 'Weekday', 'num_Postal Code', 'Hurricane', 'BadWeather']]

code_dic = NearestDict({10035: 3,
        10024: 2,
        10009: 0,
        10011: 1,
        14609: 19,
        11561: 9,
        11572: 10,
        13021: 13,
        10701: 5,
        12180: 12,
        11550: 8,
        13601: 16,
        14215: 17,
        10550: 4,
        13501: 15,
        11520: 7,
        10801: 6,
        13440: 14,
        14304: 18,
        14701: 20,
        11757: 11})

def get_prediction_features(order_id, session=Session):
    result = deliver.user(order_id=order_id, session=session)
    if not result :
        raise HTTPException(status_code=404, detail='deliver not found')
    year = result['order_date']['year']
    month = result['order_date']['month']
    weekday = result['order_date']['weekday']
    ship_mode = result['delivery_type']
    address = result['address']
    original_code = int(address.split('/')[1])

    postal_code = code_dic[original_code]
    hurricane = 0
    badweather = 0
    
    return {
        "ship_mode": ship_mode,
        "year": year,
        "month": month,
        "weekday": weekday,
        "postal_code": postal_code,
        "hurricane": hurricane,
        "badweather": badweather
    }
    # year = result['order_date']['year']
    # month = result['order_date']['month']
    # weekday = result['order_date']['weekday']
    # ship_mode = result['delivery_type']

# class InputFeatures(BaseModel):
#     ship_mode: int
#     year: int
#     month: int
#     weekday: int
#     postal_code: int
#     hurricane: int
#     badweather: int

@router.get("/duration/{order_id}", status_code=200)
async def predict_duration(order_id: str, session : Session = Depends(db.session)):
    features = get_prediction_features(order_id,session=session)
    
    duration = model.predict([[
        features["ship_mode"],
        features["year"],
        features["month"],
        features["weekday"],
        features["postal_code"],
        features["hurricane"],
        features["badweather"]
    ]])
    
    return {"predicted_value": int(duration[0])}