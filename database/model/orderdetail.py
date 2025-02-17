from sqlalchemy import Column,String,Integer, ForeignKey, Double
from sqlalchemy.orm import relationship
from database.model.base import Base
class OrderDetail(Base) :
    
    __tablename__ = 'orderdetail' # 테이블명
    __table_args__ = {'schema': 'luckydepot'} # 스키마명 

    id = Column(String, primary_key=True) 
    user_seq = Column(Integer,ForeignKey('luckydepot.user.seq')) # 외래키 user seq
    product_id = Column(Integer, ForeignKey('luckydepot.product.id')) # 외래키 product id
    price = Column(Double)
    quantity = Column(Integer) 
    name = Column(String)

    user = relationship("User", back_populates="orderdetail")
    product = relationship("Product", back_populates="orderdetail")
