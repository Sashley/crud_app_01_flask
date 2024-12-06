
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Container(Base):
    __tablename__ = 'container'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    number = Column(String, nullable=True)
    
    port_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    
    updated = Column(DateTime, nullable=True)

    # Relationships
    port = relationship("Port", foreign_keys=[port_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'number': getattr(self, 'number'),
            'port_id': getattr(self, 'port_id'),
            'updated': getattr(self, 'updated'),
            'port': getattr(self, 'port').to_dict() if getattr(self, 'port') else None,
        }