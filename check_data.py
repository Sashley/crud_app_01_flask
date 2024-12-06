from database import db_session
from generator.output.models.client import Client
from generator.output.models.vessel import Vessel
from generator.output.models.manifest import Manifest
from generator.output.models.container import Container

def check_data():
    clients = db_session.query(Client).count()
    vessels = db_session.query(Vessel).count()
    manifests = db_session.query(Manifest).count()
    containers = db_session.query(Container).count()
    
    print(f"Found:")
    print(f"Clients: {clients}")
    print(f"Vessels: {vessels}")
    print(f"Manifests: {manifests}")
    print(f"Containers: {containers}")
    
    return clients > 0 and vessels > 0 and manifests > 0 and containers > 0

if __name__ == "__main__":
    has_data = check_data()
    if not has_data:
        print("\nDatabase appears to be empty or missing data")
    else:
        print("\nDatabase contains example data")
