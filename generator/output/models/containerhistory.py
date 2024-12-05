
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class ContainerHistory(Base):
    __tablename__ = 'containerhistory'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    container_id = Column(Integer, ForeignKey("container.id"), nullable=True)
    
    port_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    
    client_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    
    container_status_id = Column(Integer, ForeignKey("containerstatus.id"), nullable=True)
    
    damage = Column(String, nullable=True)
    
    updated = Column(DateTime, nullable=True)

    # Relationships

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'container_id': getattr(self, 'container_id'),
            'port_id': getattr(self, 'port_id'),
            'client_id': getattr(self, 'client_id'),
            'container_status_id': getattr(self, 'container_status_id'),
            'damage': getattr(self, 'damage'),
            'updated': getattr(self, 'updated'),
        }