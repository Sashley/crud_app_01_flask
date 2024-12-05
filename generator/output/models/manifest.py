
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
        }