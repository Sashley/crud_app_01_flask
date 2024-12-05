
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Voyage(Base):
    __tablename__ = 'voyage'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    name = Column(String, nullable=True)
    
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=True)
    
    rotation_number = Column(Integer, nullable=True)

    # Relationships

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'name': getattr(self, 'name'),
            'vessel_id': getattr(self, 'vessel_id'),
            'rotation_number': getattr(self, 'rotation_number'),
        }