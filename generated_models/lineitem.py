from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class LineItem(Base):
    __tablename__ = 'lineitem'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    manifest_id = Column(Integer, ForeignKey("manifest.id"), nullable=True)
    
    description = Column(String, nullable=True)
    
    quantity = Column(Integer, nullable=True)
    
    weight = Column(Integer, nullable=True)
    
    volume = Column(Integer, nullable=True)
    
    pack_type_id = Column(Integer, ForeignKey("packtype.id"), nullable=True)
    
    commodity_id = Column(Integer, ForeignKey("commodity.id"), nullable=True)
    
    container_id = Column(Integer, ForeignKey("container.id"), nullable=True)
    
    manifester_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    # Relationships
    manifest = relationship("Manifest", foreign_keys=[manifest_id])
    pack_type = relationship("PackType", foreign_keys=[pack_type_id])
    commodity = relationship("Commodity", foreign_keys=[commodity_id])
    container = relationship("Container", foreign_keys=[container_id])
    manifester = relationship("User", foreign_keys=[manifester_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'manifest_id': getattr(self, 'manifest_id'),
            'description': getattr(self, 'description'),
            'quantity': getattr(self, 'quantity'),
            'weight': getattr(self, 'weight'),
            'volume': getattr(self, 'volume'),
            'pack_type_id': getattr(self, 'pack_type_id'),
            'commodity_id': getattr(self, 'commodity_id'),
            'container_id': getattr(self, 'container_id'),
            'manifester_id': getattr(self, 'manifester_id'),
            'manifest': getattr(self, 'manifest').to_dict() if getattr(self, 'manifest') else None,
            'pack_type': getattr(self, 'pack_type').to_dict() if getattr(self, 'pack_type') else None,
            'commodity': getattr(self, 'commodity').to_dict() if getattr(self, 'commodity') else None,
            'container': getattr(self, 'container').to_dict() if getattr(self, 'container') else None,
            'manifester': getattr(self, 'manifester').to_dict() if getattr(self, 'manifester') else None,
        }
