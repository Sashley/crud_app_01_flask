
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Vessel(Base):
    __tablename__ = 'vessel'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    name = Column(String, nullable=True)
    
    shipping_company_id = Column(Integer, ForeignKey("shippingcompany.id"), nullable=True)

    # Relationships

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'name': getattr(self, 'name'),
            'shipping_company_id': getattr(self, 'shipping_company_id'),
        }