from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Country(Base):
    __tablename__ = 'country'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    code = Column(String(2), nullable=False)  # ISO 2-letter country code
    region = Column(String, nullable=True)

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'name': getattr(self, 'name'),
            'code': getattr(self, 'code'),
            'region': getattr(self, 'region'),
        }
