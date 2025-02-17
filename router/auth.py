from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from static.hosts import JWT_SECRET, JWT_ALGORITHM
from database.conn.connection import db
from database.model.user import User
from database.model.admin import Admin
from static.models import SnsType, Token, UserToken, UserRegister, AdminLogin
"""
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
405 Method not allowed
500 Internal Error
502 Bad Gateway 
504 Timeout
200 OK
201 Created
"""


router = APIRouter()


@router.post("/register/{sns_type}", status_code=201, response_model=Token)
async def register(sns_type: SnsType, reg_info: UserRegister, session: Session = Depends(db.session)):
    """
    `회원가입 API`\n
    """
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(reg_info.email)
        if is_exist:
            return JSONResponse(status_code=400, content=dict(msg="EMAIL_EXISTS"))
        
        hash_pw = bcrypt.hashpw(reg_info.pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        new_user = User.create(session, auto_commit=True, pw=hash_pw, email=reg_info.email)
        
        validated_user = UserToken.model_validate(new_user)  # ORM 객체를 Pydantic 모델로 변환
        token_data = validated_user.model_dump(exclude={"pw"})  # pw 필드 제외
        token = dict(Authorization=f"Bearer {create_access_token(data=token_data)}")
        return token

    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))



@router.post("/login/{sns_type}", status_code=200, response_model=Token)
async def login(sns_type: SnsType, admin_info: AdminLogin, session : Session = Depends(db.session)):
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(admin_info.id, session)
        if not admin_info.id or not admin_info.pw:
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided'"))
        if not is_exist:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
        result = session.query(Admin).filter(Admin.id == admin_info.id).first()
        is_verified = bcrypt.checkpw(admin_info.pw.encode("utf-8"), result.pw.encode("utf-8"))
        if not is_verified:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))

        token = {
            "Authorization": f"Bearer {create_access_token(data={'id': result.id})}"
        }

        # 응답 반환
        return token
    
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


async def is_email_exist(email: str, session: Session = Depends(db.session)):
    get_email = session.query(User).filter(User.id == email)
    if get_email:
        return True
    return False


def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.now() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt
