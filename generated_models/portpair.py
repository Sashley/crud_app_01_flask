
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PortPair(Base):
    __tablename__ = 'portpair'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    pol_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    
    pod_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    
    distance = Column(Integer, nullable=True)

    # Relationships
    pol = relationship("Port", foreign_keys=[pol_id])
    pod = relationship("Port", foreign_keys=[pod_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'pol_id': getattr(self, 'pol_id'),
            'pod_id': getattr(self, 'pod_id'),
            'distance': getattr(self, 'distance'),
            'pol': getattr(self, 'pol').to_dict() if getattr(self, 'pol') else None,
            'pod': getattr(self, 'pod').to_dict() if getattr(self, 'pod') else None,
        }