
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
        }