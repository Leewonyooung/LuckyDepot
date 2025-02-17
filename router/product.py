from database.model.product import Product
from database.model.category import Category
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session
from database.conn.connection import db
from starlette.responses import FileResponse
from errors import exceptions as ex
from static.models import ProductCreate
import os, shutil

UPLOAD_FOLDER = 'crawling_img'

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
@router.get("/", status_code=200)
async def index(session: Session = Depends(db.session), keyword : str = None):
    """
    `All Product`\n
    DB에 저장된 모든 Product 정보 가져오기 \n
    :return:
    """

    if keyword != None :
        product = session.query(Product).filter(Product.name.ilike(f"%{keyword}%")).all()
        if not product :
            raise HTTPException(status_code=404, detail='product not found')
    else :
        product = session.query(Product).all()
    return {"result" :product}


# 상품 하나의 정보 가져오는 API
@router.get("/{product_id}/", status_code=200)
async def get_product_detail(product_id: int, session: Session = Depends(db.session)):
    """
    `Product by ID`\n
    ID와 일치하는 Product 정보 가져오기 \n
    :return:
    """
    product = session.query(Product).filter(Product.id == product_id).first()
    return {"result" :product}


# 카테고리 별로 상품 가져오기
@router.get("/category/{category_id}", status_code=200)
async def get_products_by_category(category_id: int, session: Session = Depends(db.session)):
    """
    `Products by Category`\n
    주어진 카테고리 ID에 속하는 모든 Product 정보 가져오기 \n
    :param category_id: 카테고리 ID
    :param session: SQLAlchemy 세션
    :return: 해당 카테고리의 상품 목록
    """
    try:
        # 카테고리 존재 여부 확인
        category = session.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        # 카테고리 ID로 상품 조회
        products = session.query(Product).filter(Product.category_id == category_id).all()
        if not products:
            raise HTTPException(status_code=404, detail="No products found for this category")

        # 결과 반환
        return {"result": [product.__dict__ for product in products]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


# 새로운 상품을 등록하는 API
@router.post("/", status_code=201)
async def create_product(product: ProductCreate, session: Session = Depends(db.session)):
    """
    `상품 등록`\n
    서비스에 새로운 상품 등록 \n
    """
    try:
        # category_id 유효성 확인
        category = session.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id. Category not found.")

        # 새로운 Product 생성
        new_product = Product(
            name=product.name,
            price=product.price,
            image=product.image,
            quantity=product.quantity,
            category_id=product.category_id
        )
        session.add(new_product)
        session.commit()
        session.refresh(new_product)

        return {"result": "생성이 성공적으로 완료되었습니다."}
    
    except Exception as e:
        import traceback
        traceback.print_exc()  # 전체 예외 출력
        raise HTTPException(status_code=500, detail=str(e))  # 원래 에러 메시지 반환




# 상품 재고 수정하는 API
@router.put("/{product_id}")
async def update_product_quantity(product_id: int, quantity: int, session: Session = Depends(db.session)):
    """
    `재고 수정`\n
    ID와 일치하는 Product quantity 수정하기 \n
    :return:
    """
    try:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ex.UpdateDataNotFoundEx() 

        product.quantity = quantity
        session.commit()
        session.refresh(product) 
        return {"result": "수정이 성공적으로 완료되었습니다."}
    
    except ex.APIException as api_ex:
        raise api_ex
    
    except Exception as e:
        raise ex.SqlFailureEx(ex=e)
    

@router.delete("/{product_id}")
async def remove_product(product_id: int, session: Session = Depends(db.session)):
    """
    `상품 삭제`\n
    ID와 일치하는 Product 삭제하기 \n
    :return:
    """
    try:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ex.DeleteDataNotFoundEx() 

        # 데이터 삭제
        session.delete(product)
        session.commit()
        return {"result": "삭제가 성공적으로 완료되었습니다."}
    
    except ex.APIException as api_ex:
        raise api_ex
    
    except Exception as e:
        raise ex.SqlFailureEx(ex=e)


@router.get("/view/{image}", response_class=FileResponse)
async def get_file(image: str):
    """
    `이미지 보기`\n
    해당 상품의 이미지 Attribute를 넣으면 이미지 반환 \n
    사용밥 : http://192.168.50.38:8000/product/view/{DB의 image column값 넣어주기}
    사용 예시 : http://192.168.50.38:8000/product/view/Tables_1.jpg
    :return:
    """
    file_path = os.path.join(UPLOAD_FOLDER, image)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="image/jpeg")


@router.post("/image/")
async def upload_file(file:UploadFile=File(...)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {'result' : 'OK'}
    except Exception as e:
        print("Error:", e)
        return{"results" : "Error"}
    
async def get_current_user(request: Request):
    """
    ✅ 미들웨어에서 검증된 사용자 정보 반환
    - 인증되지 않은 경우 401 에러 발생
    """
    print("유효한 사용자 확인")
    if not request.state.user:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")
    return request.state.user

# ✅ JWT 검증 후 전체 상품 리스트 반환
@router.get("/test/jwt-test", status_code=200)
async def get_all_products_with_jwt(
    session: Session = Depends(db.session), 
    current_user: dict = Depends(get_current_user)  # ✅ 토큰 검증된 사용자 정보 가져오기
):
    """
    ✅ JWT 인증이 필요한 API
    - 인증된 사용자만 모든 상품 리스트 조회 가능
    """
    products = session.query(Product).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    return {
        "user": current_user["email"],  # ✅ 요청한 사용자의 이메일 포함
        "products": products
    }
