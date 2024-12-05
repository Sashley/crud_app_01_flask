
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Port(Base):
    __tablename__ = 'port'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    name = Column(String, nullable=True)
    
    country_id = Column(Integer, ForeignKey("country.id"), nullable=True)
    
    prefix = Column(String, nullable=True)

    # Relationships

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'name': getattr(self, 'name'),
            'country_id': getattr(self, 'country_id'),
            'prefix': getattr(self, 'prefix'),
        }