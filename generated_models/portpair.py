from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class PortPair(Base):
    __tablename__ = 'portpair'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    pol_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    
    pod_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    
    distance = Column(Integer, nullable=True)

    distance_code = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint('distance_code >= 1 AND distance_code <= 8', name='check_distance_code_range'),
    )

    # Relationships
    pol = relationship("Port", foreign_keys=[pol_id])
    pod = relationship("Port", foreign_keys=[pod_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'pol_id': getattr(self, 'pol_id'),
            'pod_id': getattr(self, 'pod_id'),
            'distance': getattr(self, 'distance'),
            'distance_code': getattr(self, 'distance_code'),
            'pol': getattr(self, 'pol').to_dict() if getattr(self, 'pol') else None,
            'pod': getattr(self, 'pod').to_dict() if getattr(self, 'pod') else None,
        }
