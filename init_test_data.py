from database import db_session
from generator.output.models import Client, Vessel, Voyage, Port, User, Manifest
from datetime import datetime, timedelta
import random

def init_test_data():
    # Create test clients
    shipping_companies = [
        "Maersk Shipping", "MSC Global", "CMA CGM", "COSCO Shipping", 
        "Hapag-Lloyd", "ONE Line", "Evergreen Marine", "Yang Ming", 
        "HMM Co Ltd", "PIL Pacific", "ZIM Lines", "Wan Hai Lines",
        "KMTC Line", "IRISL Group", "SITC Container", "OOCL",
        "Sinotrans", "Zhonggu Shipping", "Antong Holdings", "Sinokor"
    ]
    clients = []
    for company in shipping_companies:
        client = Client(name=company)
        clients.append(client)
        db_session.add(client)
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
        vessel = Vessel(name=name)
        vessels.append(vessel)
        db_session.add(vessel)
    db_session.commit()

    # Create test voyages - ensure each vessel has at least one voyage
    voyages = []
    voyage_counter = 1
    
    # First, create one voyage for each vessel
    for vessel in vessels:
        voyage = Voyage(
            voyage_number=f"V{str(voyage_counter).zfill(3)}", 
            vessel_id=vessel.id
        )
        voyages.append(voyage)
        db_session.add(voyage)
        voyage_counter += 1
    
    # Then create additional random voyages
    remaining_voyages = 20 - len(vessels)  # Total desired - ones already created
    for i in range(remaining_voyages):
        voyage = Voyage(
            voyage_number=f"V{str(voyage_counter).zfill(3)}", 
            vessel_id=random.choice(vessels).id
        )
        voyages.append(voyage)
        db_session.add(voyage)
        voyage_counter += 1
    
    db_session.commit()

    # Create test ports
    port_data = [
        ("Port of Singapore", "SGP"), ("Port of Rotterdam", "RTM"), 
        ("Port of Shanghai", "SHA"), ("Port of Hong Kong", "HKG"),
        ("Port of Busan", "PUS"), ("Port of Los Angeles", "LAX"),
        ("Port of Long Beach", "LGB"), ("Port of Hamburg", "HAM"),
        ("Port of Antwerp", "ANR"), ("Port of Qingdao", "TAO"),
        ("Port of Dubai", "DXB"), ("Port of Tianjin", "TSN"),
        ("Port of Xiamen", "XMN"), ("Port of Kaohsiung", "KHH"),
        ("Port of New York", "NYC"), ("Port of Valencia", "VLC"),
        ("Port of Colombo", "CMB"), ("Port of Tokyo", "TYO"),
        ("Port of Barcelona", "BCN"), ("Port of Jeddah", "JED"),
        ("Port of Manila", "MNL"), ("Port of Laem Chabang", "LCH"),
        ("Port of Tanjung Pelepas", "TPP"), ("Port of Piraeus", "PIR"),
        ("Port of Ningbo", "NGB"), ("Port of Guangzhou", "CAN"),
        ("Port of Shenzhen", "SZX"), ("Port of Oakland", "OAK"),
        ("Port of Seattle", "SEA"), ("Port of Vancouver", "YVR")
    ]
    ports = []
    for name, code in port_data:
        port = Port(name=name, code=code)
        ports.append(port)
        db_session.add(port)
    db_session.commit()

    # Create test users
    user_data = [
        ("john_doe", "john@example.com"), ("jane_smith", "jane@example.com"),
        ("bob_wilson", "bob@example.com"), ("alice_brown", "alice@example.com"),
        ("charlie_davis", "charlie@example.com"), ("diana_miller", "diana@example.com"),
        ("edward_jones", "edward@example.com"), ("fiona_taylor", "fiona@example.com"),
        ("george_white", "george@example.com"), ("helen_clark", "helen@example.com"),
        ("ian_moore", "ian@example.com"), ("julia_adams", "julia@example.com"),
        ("kevin_hall", "kevin@example.com"), ("laura_wright", "laura@example.com"),
        ("mike_turner", "mike@example.com"), ("nancy_king", "nancy@example.com"),
        ("oscar_lee", "oscar@example.com"), ("patricia_hill", "patricia@example.com"),
        ("quinn_baker", "quinn@example.com"), ("rachel_ross", "rachel@example.com")
    ]
    users = []
    for username, email in user_data:
        user = User(username=username, email=email)
        users.append(user)
        db_session.add(user)
    db_session.commit()

    # Create test manifests
    start_date = datetime(2024, 1, 1)
    for i in range(30):
        # Generate a random date within 2024
        random_days = random.randint(0, 364)
        manifest_date = start_date + timedelta(days=random_days)
        
        # Randomly select different clients for shipper and consignee
        shipper = random.choice(clients)
        consignee = random.choice([c for c in clients if c != shipper])
        
        # Randomly select a vessel and one of its voyages
        vessel = random.choice(vessels)
        vessel_voyages = [v for v in voyages if v.vessel_id == vessel.id]
        voyage = random.choice(vessel_voyages)  # Now guaranteed to have at least one voyage
        
        # Randomly select different ports for loading and discharge
        port_of_loading = random.choice(ports)
        port_of_discharge = random.choice([p for p in ports if p != port_of_loading])
        
        manifest = Manifest(
            bill_of_lading=f"BL{str(i+1).zfill(3)}",
            shipper_id=shipper.id,
            consignee_id=consignee.id,
            vessel_id=vessel.id,
            voyage_id=voyage.id,
            port_of_loading_id=port_of_loading.id,
            port_of_discharge_id=port_of_discharge.id,
            place_of_delivery=f"{port_of_discharge.name} City Center",
            place_of_receipt=f"{port_of_loading.name} Terminal",
            clauses=random.choice([
                "Handle with care", 
                "Temperature controlled",
                "Fragile goods",
                "Hazardous materials",
                "Keep dry",
                "This side up",
                "Do not stack",
                "Refrigerated cargo"
            ]),
            date_of_receipt=manifest_date,
            manifester_id=random.choice(users).id
        )
        db_session.add(manifest)
    
    db_session.commit()

    print("Test data initialized successfully.")

if __name__ == "__main__":
    init_test_data()
