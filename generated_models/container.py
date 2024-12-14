from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Container(Base):
    __tablename__ = 'container'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    container_number = Column(String, nullable=True)
    container_type = Column(String, nullable=True)
    size = Column(String, nullable=True)
    max_weight = Column(Float, nullable=True)
    port_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("containerstatus.id"), nullable=True)
    updated = Column(DateTime, nullable=True)

    # Relationships
    port = relationship("Port", foreign_keys=[port_id])
    status = relationship("ContainerStatus", foreign_keys=[status_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'container_number': getattr(self, 'container_number'),
            'container_type': getattr(self, 'container_type'),
            'size': getattr(self, 'size'),
            'max_weight': getattr(self, 'max_weight'),
            'port_id': getattr(self, 'port_id'),
            'status_id': getattr(self, 'status_id'),
            'updated': getattr(self, 'updated'),
            'port': getattr(self, 'port').to_dict() if getattr(self, 'port') else None,
            'status': getattr(self, 'status').to_dict() if getattr(self, 'status') else None,
        }
