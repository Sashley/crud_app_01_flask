from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Voyage(Base):
    __tablename__ = 'voyage'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    voyage_number = Column(String, nullable=True)
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=True)
    departure_date = Column(Date, nullable=True)
    arrival_date = Column(Date, nullable=True)
    rotation_number = Column(Integer, nullable=True)

    # Relationships
    vessel = relationship("Vessel", foreign_keys=[vessel_id])

    def to_dict(self):
        return {
            'id': getattr(self, 'id'),
            'voyage_number': getattr(self, 'voyage_number'),
            'vessel_id': getattr(self, 'vessel_id'),
            'departure_date': getattr(self, 'departure_date'),
            'arrival_date': getattr(self, 'arrival_date'),
            'rotation_number': getattr(self, 'rotation_number'),
            'vessel': getattr(self, 'vessel').to_dict() if getattr(self, 'vessel') else None,
        }
