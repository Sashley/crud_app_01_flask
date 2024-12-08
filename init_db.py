from database import init_db, engine, Base
from generated_models.manifest import Manifest
from generated_models.lineitem import LineItem
from generated_models.commodity import Commodity
from generated_models.packtype import PackType
from generated_models.container import Container
from generated_models.containerhistory import ContainerHistory
from generated_models.containerstatus import ContainerStatus
from generated_models.shippingcompany import ShippingCompany
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from generated_models.leg import Leg
from generated_models.port import Port
from generated_models.portpair import PortPair
from generated_models.country import Country
from generated_models.client import Client
from generated_models.user import User
from generated_models.rate import Rate

if __name__ == '__main__':
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully.")
