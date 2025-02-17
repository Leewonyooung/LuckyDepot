from sqlalchemy import Column,String, Integer, ForeignKey, Double
from sqlalchemy.orm import relationship
from database.model.base import Base
class Product(Base) :
    
    __tablename__ = 'product' # 테이블명
    __table_args__ = {'schema': 'luckydepot'} # 스키마명 

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Double)
    image = Column(String)
    quantity = Column(Integer)
    category_id = Column(Integer, ForeignKey('luckydepot.category.id'))  # category 테이블 참조, ForeignKey

    category = relationship("Category", back_populates="product")
    orderdetail = relationship("OrderDetail", back_populates="product")
    management = relationship("Management", back_populates="product")


