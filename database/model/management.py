from sqlalchemy import Column, TIMESTAMP, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.model.base import Base
class Management(Base) :
    
    __tablename__ = 'management' # 테이블명
    __table_args__ = {'schema': 'luckydepot'} # 스키마명 

    id = Column(Integer, primary_key=True, autoincrement=True) 
    product_id = Column(Integer,ForeignKey('luckydepot.product.id')) # 외래키 설정 product테이블의 id
    hub_id = Column(Integer,ForeignKey('luckydepot.hub.id')) # 외래키 설정 hub 테이블의 id
    quantity = Column(Integer)
    change_date = Column(TIMESTAMP)
    
    product = relationship("Product", back_populates="management")
    hub = relationship("Hub", back_populates="management")
