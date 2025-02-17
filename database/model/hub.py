
from sqlalchemy import Column,String, Double, Integer
from sqlalchemy.orm import relationship
from database.model.base import Base
class Hub(Base) :
    
    __tablename__ = 'hub' # 테이블명
    __table_args__ = {'schema': 'luckydepot'} # 스키마명 

    id = Column(Integer, primary_key=True, autoincrement=True) 
    name = Column(String)
    lat = Column(Double)
    lng = Column(Double)
    manager = Column(String)
    phone = Column(String)
    mail = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    
    deliver = relationship("Deliver", back_populates="hub")
    management = relationship("Management", back_populates="hub")


