from fastapi import FastAPI, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import APIKeyHeader
from starlette.middleware.cors import CORSMiddleware
from middlewares.trusted_hosts import TrustedHostMiddleware
from database.conn import connection
from middlewares.token_validator import access_control
from static.hosts import TRUSTED_HOSTS, LUCKYDEPOT_SDK
import uvicorn

# router
from router.auth import router as auth_router
from router.product import router as product_router
from router.orderdetail import router as od_router
from router.order_router import router as order_router
from router.login import router as login_router
from router.deliver import router as deliver_router
from router.driver import router as driver_router
from router.hub import router as hub_router
from router.category import router as category_router
from router.ml_model import router as ml_router

static_dir = "../crawiling_img"
API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)

def create_app():
    """
    앱 함수 실행
    :return:
    """
    app = FastAPI()

    # 데이터 베이스 이니셜라이즈
    connection.db.init_app(app)

    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS, except_path=["/health"])
    return app


app = create_app()


app.include_router(auth_router, tags=["Auth"], prefix="/auth")
app.include_router(product_router, tags=["Product"],prefix="/product")
                #    , dependencies=[Depends(API_KEY_HEADER)])
app.include_router(od_router, tags=["Detail"], prefix="/detail")
app.include_router(order_router, tags=["Order"], prefix="/order")
app.include_router(login_router, tags=["Login"], prefix="/login")
app.include_router(deliver_router, tags=["Deliver"], prefix="/deliver")
app.include_router(hub_router, tags=["Hub"], prefix="/hub")
app.include_router(driver_router, tags=["Driver"], prefix="/driver")
app.include_router(category_router, tags=["Category"], prefix="/category")
app.include_router(ml_router, tags=["ML"], prefix="/ml")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
