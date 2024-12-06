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
    container = relationship("Container", foreign_keys=[container_id])
    port = relationship("Port", foreign_keys=[port_id])
    client = relationship("Client", foreign_keys=[client_id])
    container_status = relationship("ContainerStatus", foreign_keys=[container_status_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'container_id': getattr(self, 'container_id'),
            'port_id': getattr(self, 'port_id'),
            'client_id': getattr(self, 'client_id'),
            'container_status_id': getattr(self, 'container_status_id'),
            'damage': getattr(self, 'damage'),
            'updated': getattr(self, 'updated'),
            'container': getattr(self, 'container').to_dict() if getattr(self, 'container') else None,
            'port': getattr(self, 'port').to_dict() if getattr(self, 'port') else None,
            'client': getattr(self, 'client').to_dict() if getattr(self, 'client') else None,
            'container_status': getattr(self, 'container_status').to_dict() if getattr(self, 'container_status') else None,
        }
