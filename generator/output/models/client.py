
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Client(Base):
    __tablename__ = 'client'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    name = Column(String, nullable=True)
    
    address = Column(String, nullable=True)
    
    town = Column(String, nullable=True)
    
    country_id = Column(Integer, ForeignKey("country.id"), nullable=True)
    
    contact_person = Column(String, nullable=True)
    
    email = Column(String, nullable=True)
    
    phone = Column(String, nullable=True)

    # Relationships

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'name': getattr(self, 'name'),
            'address': getattr(self, 'address'),
            'town': getattr(self, 'town'),
            'country_id': getattr(self, 'country_id'),
            'contact_person': getattr(self, 'contact_person'),
            'email': getattr(self, 'email'),
            'phone': getattr(self, 'phone'),
        }