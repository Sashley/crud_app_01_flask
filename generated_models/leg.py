
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Leg(Base):
    __tablename__ = 'leg'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    voyage_id = Column(Integer, ForeignKey("voyage.id"), nullable=True)
    
    port_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    
    leg_number = Column(Integer, nullable=True)
    
    eta = Column(DateTime, nullable=True)
    
    etd = Column(DateTime, nullable=True)

    # Relationships
    voyage = relationship("Voyage", foreign_keys=[voyage_id])
    port = relationship("Port", foreign_keys=[port_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'voyage_id': getattr(self, 'voyage_id'),
            'port_id': getattr(self, 'port_id'),
            'leg_number': getattr(self, 'leg_number'),
            'eta': getattr(self, 'eta'),
            'etd': getattr(self, 'etd'),
            'voyage': getattr(self, 'voyage').to_dict() if getattr(self, 'voyage') else None,
            'port': getattr(self, 'port').to_dict() if getattr(self, 'port') else None,
        }