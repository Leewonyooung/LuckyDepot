from sqlalchemy import Column,String
from database.model.base import Base

class Admin(Base):
    __tablename__ = 'admin'  # 테이블명
    __table_args__ = {'schema': 'luckydepot'} # 스키마명 
    id = Column(String, primary_key=True)
    pw = Column(String)
    name = Column(String)
    phone_number = Column(String)
    