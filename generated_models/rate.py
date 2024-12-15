from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class Rate(Base):
    __tablename__ = 'rate'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    distance_code = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint('distance_code >= 1 AND distance_code <= 8', name='check_rate_distance_code_range'),
    )
    
    commodity_id = Column(Integer, ForeignKey("commodity.id"), nullable=True)
    
    pack_type_id = Column(Integer, ForeignKey("packtype.id"), nullable=True)
    
    client_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    
    rate = Column(Float, nullable=True)
    
    effective = Column(DateTime, nullable=True)

    # Relationships
    commodity = relationship("Commodity", foreign_keys=[commodity_id])
    pack_type = relationship("PackType", foreign_keys=[pack_type_id])
    client = relationship("Client", foreign_keys=[client_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'distance_code': getattr(self, 'distance_code'),
            'commodity_id': getattr(self, 'commodity_id'),
            'pack_type_id': getattr(self, 'pack_type_id'),
            'client_id': getattr(self, 'client_id'),
            'rate': getattr(self, 'rate'),
            'effective': getattr(self, 'effective'),
            'commodity': getattr(self, 'commodity').to_dict() if getattr(self, 'commodity') else None,
            'pack_type': getattr(self, 'pack_type').to_dict() if getattr(self, 'pack_type') else None,
            'client': getattr(self, 'client').to_dict() if getattr(self, 'client') else None,
        }
