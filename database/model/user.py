from sqlalchemy import Column,String, Integer
from sqlalchemy.orm import relationship
from database.model.base import Base

class User(Base):
    __tablename__ = 'user'  # 테이블명
    __table_args__ = {'schema': 'luckydepot'} # 스키마명 
    seq = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String)
    name = Column(String)
    login_type = Column(String)
    
    order = relationship("Order", back_populates="user") # 관계 표시, sql쿼리 없이 관련된 테이블 접근 가능,  데이터 동기화
    orderdetail = relationship("OrderDetail", back_populates="user") # Class이름, back_populates : orderdetail.user로 user 참조 가능
