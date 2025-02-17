from sqlalchemy import Column,String, TIMESTAMP, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.model.base import Base

class Deliver(Base) :
    
    __tablename__ = 'deliver' # 테이블명
    __table_args__ = {'schema': 'luckydepot'} # 스키마명 

    id = Column(String, primary_key=True, nullable=False)
    driver_seq = Column(Integer, ForeignKey('luckydepot.driver.seq'), nullable=False) # 외래키 dirver seq
    hub_id = Column(Integer, ForeignKey('luckydepot.hub.id'), nullable=False) # 외래키 설정 hub 테이블 id
    truck_id = Column(String, ForeignKey('luckydepot.truck.id'), nullable=False) # 외래키 설정 truck 테이블 id
    order_id = Column(String)
    start_date = Column(TIMESTAMP)
    end_date = Column(TIMESTAMP)
    delivery_type = Column(Integer)

    driver = relationship("Driver", back_populates="deliver")
    hub = relationship("Hub", back_populates="deliver")
    truck = relationship("Truck", back_populates="deliver")

    

