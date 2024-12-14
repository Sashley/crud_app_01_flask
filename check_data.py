from database import db_session
from generated_models.client import Client
from generated_models.commodity import Commodity
from generated_models.containerstatus import ContainerStatus
from generated_models.country import Country
from generated_models.packtype import PackType
from generated_models.port import Port
from generated_models.shippingcompany import ShippingCompany
from generated_models.user import User
from generated_models.portpair import PortPair
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from generated_models.container import Container
from generated_models.leg import Leg
from generated_models.containerhistory import ContainerHistory
from generated_models.manifest import Manifest
from generated_models.lineitem import LineItem
from generated_models.rate import Rate

def check_table_counts():
    print("Checking record counts for all tables...")
    print("\nSequence 1:")
    print(f"Clients: {db_session.query(Client).count()} (min: 300)")
    print(f"Commodities: {db_session.query(Commodity).count()} (min: 50)")
    print(f"Container Statuses: {db_session.query(ContainerStatus).count()} (min: 15)")
    print(f"Countries: {db_session.query(Country).count()} (min: 20)")
    print(f"Pack Types: {db_session.query(PackType).count()} (min: 40)")
    print(f"Ports: {db_session.query(Port).count()} (min: 20)")
    print(f"Shipping Companies: {db_session.query(ShippingCompany).count()} (min: 3)")
    print(f"Users: {db_session.query(User).count()} (min: 5)")
    
    print("\nSequence 2:")
    print(f"Port Pairs: {db_session.query(PortPair).count()} (min: 50)")
    print(f"Vessels: {db_session.query(Vessel).count()} (min: 15)")
    
    print("\nSequence 3:")
    print(f"Voyages: {db_session.query(Voyage).count()} (min: 100)")
    
    print("\nSequence 4:")
    print(f"Containers: {db_session.query(Container).count()} (min: 1000)")
    print(f"Legs: {db_session.query(Leg).count()} (min: 500)")
    
    print("\nSequence 5:")
    print(f"Container Histories: {db_session.query(ContainerHistory).count()} (min: 15000)")
    
    print("\nSequence 6:")
    print(f"Manifests: {db_session.query(Manifest).count()} (min: 1000)")
    
    print("\nSequence 7:")
    print(f"Line Items: {db_session.query(LineItem).count()} (min: 3000)")
    print(f"Rates: {db_session.query(Rate).count()} (min: 10000)")

if __name__ == '__main__':
    check_table_counts()
    db_session.close()
