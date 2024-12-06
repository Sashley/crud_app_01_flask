from database import init_db, engine, Base
from generator.output.models.manifest import Manifest
from generator.output.models.lineitem import LineItem
from generator.output.models.commodity import Commodity
from generator.output.models.packtype import PackType
from generator.output.models.container import Container
from generator.output.models.containerhistory import ContainerHistory
from generator.output.models.containerstatus import ContainerStatus
from generator.output.models.shippingcompany import ShippingCompany
from generator.output.models.vessel import Vessel
from generator.output.models.voyage import Voyage
from generator.output.models.leg import Leg
from generator.output.models.port import Port
from generator.output.models.portpair import PortPair
from generator.output.models.country import Country
from generator.output.models.client import Client
from generator.output.models.user import User
from generator.output.models.rate import Rate

if __name__ == '__main__':
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully.")
