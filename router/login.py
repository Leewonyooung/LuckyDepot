from database.model.user import User
from database.model.category import Category
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.conn.connection import db
from errors import exceptions as ex
from static.models import LoginRequest, SeqRequest
from static.hosts import firebase_auth


router = APIRouter()

"""
    get : 조회 // status:200
    post : 생성, 개인정보 조회 // status:201
    put : 수정 //    기존 리소스가 수정된 경우: 200 (OK)
                    전송 성공 후 자원이 생성됬을 경우: 201 (Created)
                    전송은 했지만 전송할 데이터가 없는 경우: 204 (No Content)
    delete : 삭제
"""

# 모든 상품 가져오는 API
@router.post("/", status_code=200)
async def index(user = LoginRequest, session: Session = Depends(db.session)):
    """
    `구글 로그인`\n
    DB에 저장된 중복 유저가 있나 확인하고  \n
    없다면 DB에 저장하고 반환
    :return:
    """
    
    # return {"result" :product}



@router.post("/google")
async def google_login(request: LoginRequest, session: Session = Depends(db.session)):
    """
    ✅ Firebase JWT 검증 후 로그인 처리
    """
    id_token = request.idToken

    if not id_token:
        print("❌ ID Token이 없음")
        raise HTTPException(status_code=400, detail="ID Token is missing")

    print(f"📡 Received JWT Token: {id_token}")

    try:
        # ✅ Firebase ID 토큰 검증
        decoded_token = firebase_auth.verify_id_token(id_token, check_revoked=True)
        name = decoded_token.get("name", "Unknown")
        email = decoded_token.get("email")

        if not email:
            print("❌ 이메일 정보 없음")
            raise HTTPException(status_code=401, detail="Invalid Firebase ID token")

        # ✅ DB에서 사용자 검색 또는 새 사용자 추가
        user = session.query(User).filter(User.id == email).first()
        if not user:
            new_user = User(id=email, name=name, login_type="google")
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            user = new_user
            print(f"🆕 새로운 사용자 추가됨: {user.name}")

        # ✅ 응답 반환 (유효한 사용자 정보)
        return {
            "user": {
                "id": user.id,
                "seq": user.seq,
                "name": user.name
            }
        }

    except firebase_auth.ExpiredIdTokenError:
        print("❌ 만료된 토큰")
        raise HTTPException(status_code=401, detail="Expired ID token")
    except firebase_auth.InvalidIdTokenError:
        print("❌ 잘못된 토큰")
        raise HTTPException(status_code=401, detail="Invalid ID token")
    except Exception as e:
        print(f"❌ Firebase 토큰 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Firebase token error: {str(e)}")




# 로그인한 유저의 seq컬럼 값 가져오기
@router.post("/seq", status_code=200)
async def index(request = SeqRequest, session: Session = Depends(db.session)):
    """
    `유저의 seq 가져오기`\n
    DB에 저장된 id값과 비교하여 일치하는 유저의 seq값 리턴
    :return:
    result : {seq}
    """
    user = session.query(User).filter(User.id == request).first()
    if not user:
        return {"result" : "일치하는 사용자가 없습니다."}
    return {"result" : user.seq,}


@router.post("/facebook")
async def facebook_login(request: LoginRequest, session: Session = Depends(db.session)):
    """
    ✅ Facebook 로그인 처리 (Firebase JWT 검증)
    """
    id_token = request.idToken

    if not id_token:
        print("❌ ID Token이 없음")
        raise HTTPException(status_code=400, detail="ID Token is missing")

    try:
        # ✅ Firebase ID 토큰 검증
        decoded_token = firebase_auth.verify_id_token(id_token, check_revoked=True)
        name = decoded_token.get("name", "Unknown")
        email = decoded_token.get("email")

        if not email:
            print("❌ 이메일 정보 없음")
            raise HTTPException(status_code=401, detail="Invalid Firebase ID token")

        # ✅ DB에서 사용자 검색 또는 새 사용자 추가
        user = session.query(User).filter(User.id == email).first()
        if not user:
            new_user = User(id=email, name=name, login_type="facebook")
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            user = new_user

        # ✅ 응답 반환 (유효한 사용자 정보)
        return {
            "user": {
                "id": user.id,
                "seq": user.seq,
                "name": user.name
            }
        }

    except firebase_auth.ExpiredIdTokenError:
        print("❌ 만료된 토큰")
        raise HTTPException(status_code=401, detail="Expired ID token")
    except firebase_auth.InvalidIdTokenError:
        print("❌ 잘못된 토큰")
        raise HTTPException(status_code=401, detail="Invalid ID token")
    except Exception as e:
        print(f"❌ Firebase 토큰 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Firebase token error: {str(e)}")
