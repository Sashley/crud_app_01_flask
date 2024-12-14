from database import db_session
from generated_models.client import Client
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from generated_models.port import Port
from generated_models.user import User
from generated_models.manifest import Manifest
from generated_models.country import Country
from generated_models.containerstatus import ContainerStatus
from generated_models.packtype import PackType
from generated_models.commodity import Commodity
from generated_models.container import Container
from generated_models.lineitem import LineItem
from generated_models.containerhistory import ContainerHistory
from generated_models.portpair import PortPair
from generated_models.rate import Rate
from generated_models.shippingcompany import ShippingCompany
from datetime import datetime, timedelta
import random
import hashlib

def init_test_data():
    # Create test clients
    client_names = [
        "Global Shipping Co", "Ocean Traders Ltd", "Maritime Solutions Inc",
        "Pacific Logistics", "Atlantic Freight Services", "Cargo Masters",
        "Sea Routes International", "Continental Shipping", "Marine Express",
        "Worldwide Cargo Systems"
    ]
    clients = []
    for name in client_names:
        client = Client(
            name=name,
            address=f"{random.randint(1, 999)} {random.choice(['Port', 'Harbor', 'Ocean', 'Marine'])} Street",
            contact_person=f"{random.choice(['John', 'Jane', 'Mike', 'Sarah'])} {random.choice(['Smith', 'Johnson', 'Brown', 'Davis'])}",
            email=f"contact@{name.lower().replace(' ', '')}.com",
            phone=f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        )
        clients.append(client)
        db_session.add(client)
    db_session.commit()

    # Create test ports
    port_names = [
        "Port of Los Angeles", "Port of Long Beach", "Port of Oakland", 
        "Port of Seattle", "Port of Miami", "Port of New York",
        "Port of Houston", "Port of Savannah", "Port of Charleston"
    ]
    ports = []
    for name in port_names:
        port = Port(name=name)
        ports.append(port)
        db_session.add(port)
    db_session.commit()

    # Create container statuses
    status_names = [
        "Available", "In Use", "Under Repair", "Out of Service",
        "Reserved", "In Transit", "Loading", "Unloading"
    ]
    statuses = []
    for name in status_names:
        status = ContainerStatus(
            name=name,
            description=f"Container is {name.lower()}"
        )
        statuses.append(status)
        db_session.add(status)
    db_session.commit()

    # Create shipping companies
    shipping_company_names = [
        "Maersk Line", "MSC", "CMA CGM", "COSCO Shipping", 
        "Hapag-Lloyd", "ONE", "Evergreen Marine", "Yang Ming", 
        "HMM", "PIL", "ZIM", "Wan Hai Lines",
        "KMTC", "IRISL Group", "SITC", "OOCL",
        "Sinotrans", "Zhonggu Shipping", "Antong Holdings", "Sinokor"
    ]
    shipping_companies = []
    for name in shipping_company_names:
        company = ShippingCompany(name=name)
        shipping_companies.append(company)
        db_session.add(company)
    db_session.commit()

    # Create test vessels
    vessel_names = [
        "Ever Given", "MSC Oscar", "HMM Algeciras", "CMA CGM Antoine",
        "OOCL Hong Kong", "MSC Gulsun", "COSCO Universe", "MOL Triumph",
        "Madrid Maersk", "CMA CGM Brazil", "MSC Isabella", "Ever Glory",
        "HMM Copenhagen", "ONE Trust", "Yang Ming Warranty", "MSC Mia",
        "CMA CGM Palais Royal", "Hapag Hamburg", "COSCO Shipping Planet", "Ever Excel"
    ]
    vessels = []
    for name in vessel_names:
        vessel = Vessel(
            name=name,
            shipping_company_id=random.choice(shipping_companies).id
        )
        vessels.append(vessel)
        db_session.add(vessel)
    db_session.commit()

    # Create test voyages - ensure each vessel has at least one voyage
    voyages = []
    voyage_counter = 1
    start_date = datetime(2024, 1, 1)
    
    # First, create one voyage for each vessel
    for vessel in vessels:
        departure_date = start_date + timedelta(days=random.randint(0, 30))
        arrival_date = departure_date + timedelta(days=random.randint(5, 15))
        
        voyage = Voyage(
            voyage_number=f"V{str(voyage_counter).zfill(3)}",  # V001, V002, etc.
            vessel_id=vessel.id,
            departure_date=departure_date,
            arrival_date=arrival_date,
            rotation_number=voyage_counter
        )
        voyages.append(voyage)
        db_session.add(voyage)
        voyage_counter += 1
    
    # Then create additional random voyages
    remaining_voyages = 20 - len(vessels)  # Total desired - ones already created
    for i in range(remaining_voyages):
        departure_date = start_date + timedelta(days=random.randint(0, 30))
        arrival_date = departure_date + timedelta(days=random.randint(5, 15))
        
        voyage = Voyage(
            voyage_number=f"V{str(voyage_counter).zfill(3)}", 
            vessel_id=random.choice(vessels).id,
            departure_date=departure_date,
            arrival_date=arrival_date,
            rotation_number=voyage_counter
        )
        voyages.append(voyage)
        db_session.add(voyage)
        voyage_counter += 1
    
    db_session.commit()

    # Create test users
    user_names = [
        "John Smith", "Jane Doe", "Mike Johnson", "Sarah Wilson",
        "David Brown", "Lisa Davis", "Robert Miller", "Emily Anderson"
    ]
    users = []
    for name in user_names:
        user = User(
            name=name,
            email=f"{name.lower().replace(' ', '.')}@example.com",
            password_hash=hashlib.sha256(b"password123").hexdigest()
        )
        users.append(user)
        db_session.add(user)
    db_session.commit()

    # Create test manifests
    for i in range(20):  # Create 20 test manifests
        shipper = random.choice(clients)
        consignee = random.choice(clients)
        while consignee == shipper:  # Ensure different shipper and consignee
            consignee = random.choice(clients)
            
        voyage = random.choice(voyages)
        manifest = Manifest(
            bill_of_lading=f"BL{str(i+1).zfill(6)}",  # BL000001, BL000002, etc.
            shipper_id=shipper.id,
            consignee_id=consignee.id,
            vessel_id=voyage.vessel_id,
            voyage_id=voyage.id,
            port_of_loading_id=random.choice(ports).id,
            port_of_discharge_id=random.choice(ports).id,
            place_of_delivery=f"{random.choice(['Los Angeles', 'New York', 'Miami', 'Seattle', 'Houston'])} Terminal",
            place_of_receipt=f"{random.choice(['Shanghai', 'Singapore', 'Rotterdam', 'Dubai', 'Tokyo'])} Port",
            clauses="Standard shipping terms and conditions apply",
            date_of_receipt=datetime.now() - timedelta(days=random.randint(0, 30)),
            manifester_id=random.choice(users).id
        )
        db_session.add(manifest)
    
    db_session.commit()

    # Create test containers
    container_types = ["Dry", "Reefer", "Open Top", "Flat Rack", "Tank"]
    container_sizes = ["20'", "40'", "40'HC", "45'HC"]
    containers = []
    
    for i in range(20):  # Create 20 test containers
        container_number = f"CONT{str(i+1).zfill(6)}"  # CONT000001, CONT000002, etc.
        container = Container(
            container_number=container_number,
            container_type=random.choice(container_types),
            size=random.choice(container_sizes),
            max_weight=random.randint(20000, 40000),  # Random weight between 20-40 tons
            status_id=random.choice(statuses).id,
            updated=datetime.now()
        )
        containers.append(container)
        db_session.add(container)
    
    db_session.commit()

    # Create test container history records
    # Create multiple history records for each container
    for container in containers:
        # Create 3-5 history records per container
        num_records = random.randint(3, 5)
        base_date = datetime.now() - timedelta(days=30)  # Start from 30 days ago
        
        for j in range(num_records):
            record_date = base_date + timedelta(days=j*7)  # One record per week
            history = ContainerHistory(
                container_id=container.id,
                container_status_id=random.choice(statuses).id,
                port_id=random.choice(ports).id,
                damage=random.choice([None, "Minor scratch", "Dent on side", "Paint damage"]),
                updated=record_date
            )
            db_session.add(history)
    
    db_session.commit()
    print("Test data initialized successfully.")

if __name__ == "__main__":
    init_test_data()
