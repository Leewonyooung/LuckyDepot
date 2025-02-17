from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from static import hosts
from database.model import deliver,driver,hub,order,orderdetail,product,truck,user,management,admin
import logging

class SQLAlchemy:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._engine = None
        self._session = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI):
        """
        DB 초기화 함수
        :param app: FastAPI 인스턴스
        :param kwargs:
        :return:
        """
        database_url = f'postgresql://root:qwer1234@{hosts.POSTGRESQL_HOST}:30146/postgres'
        # postgresql://유저이름:비밀번호@ip주소:port/데이터베이스이름
        pool_recycle = 900

        self._engine = create_engine(
            database_url,
            echo=False,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )
        
        self._session = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

        # FastAPI lifespan으로 DB 연결 관리
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            self._engine.connect()
            logging.info("DB connected.")
            yield  # 애플리케이션 실행
            self._session.close_all()
            self._engine.dispose()
            logging.info("DB disconnected.")

        app.router.lifespan = lifespan

    def get_db(self):
        """
        요청마다 DB 세션 유지 함수
        :return:
        """
        if self._session is None:
            raise Exception("must be called 'init_app'")
        db_session = None
        try:
            db_session = self._session()
            yield db_session
        finally:
            db_session.close()

    @property
    def session(self):
        return self.get_db

    @property
    def engine(self):
        return self._engine


db = SQLAlchemy()