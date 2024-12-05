
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PackType(Base):
    __tablename__ = 'packtype'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    name = Column(String, nullable=True)
    
    description = Column(String, nullable=True)

    # Relationships

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'name': getattr(self, 'name'),
            'description': getattr(self, 'description'),
        }