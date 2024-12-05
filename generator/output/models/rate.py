
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Rate(Base):
    __tablename__ = 'rate'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    distance = Column(Integer, nullable=True)
    
    commodity_id = Column(Integer, ForeignKey("commodity.id"), nullable=True)
    
    pack_type_id = Column(Integer, ForeignKey("packtype.id"), nullable=True)
    
    client_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    
    rate = Column(Float, nullable=True)
    
    effective = Column(DateTime, nullable=True)

    # Relationships

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'distance': getattr(self, 'distance'),
            'commodity_id': getattr(self, 'commodity_id'),
            'pack_type_id': getattr(self, 'pack_type_id'),
            'client_id': getattr(self, 'client_id'),
            'rate': getattr(self, 'rate'),
            'effective': getattr(self, 'effective'),
        }