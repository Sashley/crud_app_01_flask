
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Manifest(Base):
    __tablename__ = 'manifest'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    bill_of_lading = Column(String, nullable=True)
    
    shipper_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    
    consignee_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=True)
    
    voyage_id = Column(Integer, ForeignKey("voyage.id"), nullable=True)
    
    port_of_loading_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    
    port_of_discharge_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    
    place_of_delivery = Column(String, nullable=True)
    
    place_of_receipt = Column(String, nullable=True)
    
    clauses = Column(String, nullable=True)
    
    date_of_receipt = Column(DateTime, nullable=True)
    
    manifester_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    # Relationships
    shipper = relationship("Client", foreign_keys=[shipper_id])
    consignee = relationship("Client", foreign_keys=[consignee_id])
    vessel = relationship("Vessel", foreign_keys=[vessel_id])
    voyage = relationship("Voyage", foreign_keys=[voyage_id])
    port_of_loading = relationship("Port", foreign_keys=[port_of_loading_id])
    port_of_discharge = relationship("Port", foreign_keys=[port_of_discharge_id])
    manifester = relationship("User", foreign_keys=[manifester_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'bill_of_lading': getattr(self, 'bill_of_lading'),
            'shipper_id': getattr(self, 'shipper_id'),
            'consignee_id': getattr(self, 'consignee_id'),
            'vessel_id': getattr(self, 'vessel_id'),
            'voyage_id': getattr(self, 'voyage_id'),
            'port_of_loading_id': getattr(self, 'port_of_loading_id'),
            'port_of_discharge_id': getattr(self, 'port_of_discharge_id'),
            'place_of_delivery': getattr(self, 'place_of_delivery'),
            'place_of_receipt': getattr(self, 'place_of_receipt'),
            'clauses': getattr(self, 'clauses'),
            'date_of_receipt': getattr(self, 'date_of_receipt'),
            'manifester_id': getattr(self, 'manifester_id'),
            'shipper': getattr(self, 'shipper').to_dict() if getattr(self, 'shipper') else None,
            'consignee': getattr(self, 'consignee').to_dict() if getattr(self, 'consignee') else None,
            'vessel': getattr(self, 'vessel').to_dict() if getattr(self, 'vessel') else None,
            'voyage': getattr(self, 'voyage').to_dict() if getattr(self, 'voyage') else None,
            'port_of_loading': getattr(self, 'port_of_loading').to_dict() if getattr(self, 'port_of_loading') else None,
            'port_of_discharge': getattr(self, 'port_of_discharge').to_dict() if getattr(self, 'port_of_discharge') else None,
            'manifester': getattr(self, 'manifester').to_dict() if getattr(self, 'manifester') else None,
        }