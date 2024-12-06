from database import db_session
from generator.output.models.client import Client
from generator.output.models.vessel import Vessel
from generator.output.models.voyage import Voyage
from generator.output.models.port import Port
from generator.output.models.user import User
from generator.output.models.manifest import Manifest
from generator.output.models.country import Country
from generator.output.models.containerstatus import ContainerStatus
from generator.output.models.packtype import PackType
from generator.output.models.commodity import Commodity
from generator.output.models.container import Container
from generator.output.models.lineitem import LineItem
from generator.output.models.containerhistory import ContainerHistory
from generator.output.models.portpair import PortPair
from generator.output.models.rate import Rate
from generator.output.models.shippingcompany import ShippingCompany
from datetime import datetime, timedelta
import random
import hashlib

def init_test_data():
    # Create container statuses
    status_data = [
        ("Empty", "Container is empty and available"),
        ("Loaded", "Container is loaded with cargo"),
        ("In Transit", "Container is in transit"),
        ("At Port", "Container is at port facility"),
        ("Under Inspection", "Container is being inspected"),
        ("Damaged", "Container is damaged and needs repair"),
        ("Out of Service", "Container is not available for use"),
        ("Reserved", "Container is reserved for upcoming shipment"),
        ("Cleaning", "Container is being cleaned"),
        ("Maintenance", "Container is under maintenance")
    ]
    container_statuses = []
    for name, description in status_data:
        status = ContainerStatus(name=name, description=description)
        container_statuses.append(status)
        db_session.add(status)
    db_session.commit()

    # Create pack types
    packtype_data = [
        ("Pallet", "Standard wooden pallet"),
        ("Carton", "Cardboard box"),
        ("Crate", "Wooden crate"),
        ("Drum", "Metal or plastic drum"),
        ("Bag", "Flexible container bag"),
        ("Bundle", "Bundled items"),
        ("Roll", "Rolled materials"),
        ("Case", "Protective case"),
        ("Barrel", "Storage barrel"),
        ("Loose", "Loose items")
    ]
    packtypes = []
    for name, description in packtype_data:
        packtype = PackType(name=name, description=description)
        packtypes.append(packtype)
        db_session.add(packtype)
    db_session.commit()

    # Create commodities
    commodity_data = [
        ("Electronics", "Consumer and industrial electronic goods"),
        ("Textiles", "Clothing and fabric materials"),
        ("Machinery", "Industrial machinery and parts"),
        ("Automotive Parts", "Vehicle components and spare parts"),
        ("Chemicals", "Industrial and consumer chemicals"),
        ("Food Products", "Processed and packaged foods"),
        ("Raw Materials", "Industrial raw materials"),
        ("Furniture", "Home and office furniture"),
        ("Medical Supplies", "Healthcare equipment and supplies"),
        ("Construction Materials", "Building and construction supplies")
    ]
    commodities = []
    for name, description in commodity_data:
        commodity = Commodity(name=name, description=description)
        commodities.append(commodity)
        db_session.add(commodity)
    db_session.commit()

    # Create test countries
    country_data = [
        "United States", "China", "Japan", "Germany", "United Kingdom",
        "France", "India", "Italy", "Canada", "South Korea",
        "Russia", "Brazil", "Australia", "Spain", "Mexico",
        "Indonesia", "Netherlands", "Saudi Arabia", "Switzerland", "Singapore"
    ]
    countries = []
    for name in country_data:
        country = Country(name=name)
        countries.append(country)
        db_session.add(country)
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

    # Create test clients
    client_names = [
        "Global Trade Co", "International Logistics Ltd", "Worldwide Freight Inc", "Ocean Cargo Systems", 
        "Maritime Solutions", "Pacific Trading Group", "Atlantic Shipping LLC", "Continental Carriers",
        "Express Freight Services", "Sea Route Logistics", "Cargo Masters Inc", "Marine Transport Co",
        "Global Supply Chain", "International Cargo", "World Shipping Lines", "Ocean Transport Group",
        "Maritime Logistics", "Pacific Freight", "Atlantic Cargo", "Continental Shipping"
    ]
    clients = []
    for company in client_names:
        client = Client(
            name=company,
            address=f"{company} HQ, 123 Shipping Street",
            town="Port City",
            country_id=random.choice(countries).id,  # Randomly assign a country
            contact_person=f"{company.split()[0]} Manager",
            email=f"contact@{company.lower().replace(' ', '')}.com",
            phone=f"+1-555-{random.randint(1000, 9999)}"
        )
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
        vessel = Vessel(
            name=name,
            shipping_company_id=random.choice(shipping_companies).id  # Assign to a random shipping company
        )
        vessels.append(vessel)
        db_session.add(vessel)
    db_session.commit()

    # Create test voyages - ensure each vessel has at least one voyage
    voyages = []
    voyage_counter = 1
    
    # First, create one voyage for each vessel
    for vessel in vessels:
        voyage = Voyage(
            name=f"V{str(voyage_counter).zfill(3)}",  # V001, V002, etc.
            vessel_id=vessel.id,
            rotation_number=voyage_counter  # Use counter as rotation number
        )
        voyages.append(voyage)
        db_session.add(voyage)
        voyage_counter += 1
    
    # Then create additional random voyages
    remaining_voyages = 20 - len(vessels)  # Total desired - ones already created
    for i in range(remaining_voyages):
        voyage = Voyage(
            name=f"V{str(voyage_counter).zfill(3)}", 
            vessel_id=random.choice(vessels).id,
            rotation_number=voyage_counter
        )
        voyages.append(voyage)
        db_session.add(voyage)
        voyage_counter += 1
    
    db_session.commit()

    # Create test ports with country associations
    port_data = [
        ("Port of Singapore", "SGP", "Singapore"),
        ("Port of Rotterdam", "RTM", "Netherlands"),
        ("Port of Shanghai", "SHA", "China"),
        ("Port of Hong Kong", "HKG", "China"),
        ("Port of Busan", "PUS", "South Korea"),
        ("Port of Los Angeles", "LAX", "United States"),
        ("Port of Long Beach", "LGB", "United States"),
        ("Port of Hamburg", "HAM", "Germany"),
        ("Port of Antwerp", "ANR", "Netherlands"),
        ("Port of Qingdao", "TAO", "China"),
        ("Port of Dubai", "DXB", "Saudi Arabia"),  # Using Saudi Arabia as UAE not in country list
        ("Port of Tianjin", "TSN", "China"),
        ("Port of Xiamen", "XMN", "China"),
        ("Port of Kaohsiung", "KHH", "China"),  # Using China as Taiwan not in country list
        ("Port of New York", "NYC", "United States"),
        ("Port of Valencia", "VLC", "Spain"),
        ("Port of Colombo", "CMB", "India"),  # Using India as Sri Lanka not in country list
        ("Port of Tokyo", "TYO", "Japan"),
        ("Port of Barcelona", "BCN", "Spain"),
        ("Port of Jeddah", "JED", "Saudi Arabia"),
        ("Port of Manila", "MNL", "Indonesia"),  # Using Indonesia as Philippines not in country list
        ("Port of Laem Chabang", "LCH", "India"),  # Using India as Thailand not in country list
        ("Port of Tanjung Pelepas", "TPP", "Indonesia"),  # Using Indonesia as Malaysia not in country list
        ("Port of Piraeus", "PIR", "Italy"),  # Using Italy as Greece not in country list
        ("Port of Ningbo", "NGB", "China"),
        ("Port of Guangzhou", "CAN", "China"),
        ("Port of Shenzhen", "SZX", "China"),
        ("Port of Oakland", "OAK", "United States"),
        ("Port of Seattle", "SEA", "United States"),
        ("Port of Vancouver", "YVR", "Canada")
    ]
    ports = []
    # Create a dictionary to map country names to IDs
    country_map = {country.name: country.id for country in countries}
    
    for name, prefix, country_name in port_data:
        port = Port(
            name=name,
            prefix=prefix,
            country_id=country_map[country_name]
        )
        ports.append(port)
        db_session.add(port)
    db_session.commit()

    # Create port pairs with realistic distances
    for pol in ports:
        for pod in ports:
            if pol != pod:  # Don't create pairs for same port
                # Generate a semi-realistic distance (nautical miles)
                # Basic formula: random base distance + factor based on port codes
                base_distance = random.randint(500, 8000)
                port_pair = PortPair(
                    pol_id=pol.id,
                    pod_id=pod.id,
                    distance=base_distance
                )
                db_session.add(port_pair)
    db_session.commit()

    # Create test users
    user_data = [
        ("John Doe", "john@example.com"), ("Jane Smith", "jane@example.com"),
        ("Bob Wilson", "bob@example.com"), ("Alice Brown", "alice@example.com"),
        ("Charlie Davis", "charlie@example.com"), ("Diana Miller", "diana@example.com"),
        ("Edward Jones", "edward@example.com"), ("Fiona Taylor", "fiona@example.com"),
        ("George White", "george@example.com"), ("Helen Clark", "helen@example.com"),
        ("Ian Moore", "ian@example.com"), ("Julia Adams", "julia@example.com"),
        ("Kevin Hall", "kevin@example.com"), ("Laura Wright", "laura@example.com"),
        ("Mike Turner", "mike@example.com"), ("Nancy King", "nancy@example.com"),
        ("Oscar Lee", "oscar@example.com"), ("Patricia Hill", "patricia@example.com"),
        ("Quinn Baker", "quinn@example.com"), ("Rachel Ross", "rachel@example.com")
    ]
    users = []
    for name, email in user_data:
        # Create a simple password hash (in production, use proper password hashing)
        password_hash = hashlib.sha256(f"password123_{email}".encode()).hexdigest()
        user = User(
            name=name,
            email=email,
            password_hash=password_hash
        )
        users.append(user)
        db_session.add(user)
    db_session.commit()

    # Create test manifests
    start_date = datetime(2024, 1, 1)
    manifests = []
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
        manifests.append(manifest)
        db_session.add(manifest)
    
    db_session.commit()

    # Create test containers
    containers = []
    for i in range(50):  # Create 50 containers
        container = Container(
            number=f"CONT{str(i+1).zfill(6)}",  # CONT000001, CONT000002, etc.
            port_id=random.choice(ports).id,  # Randomly assign to a port
            updated=datetime.now() - timedelta(days=random.randint(0, 30))  # Random date within last 30 days
        )
        containers.append(container)
        db_session.add(container)
    db_session.commit()

    # Create test line items
    for manifest in manifests:
        # Create 1-5 line items per manifest
        for _ in range(random.randint(1, 5)):
            line_item = LineItem(
                manifest_id=manifest.id,
                description=f"Shipment of {random.choice(commodities).name.lower()}",
                quantity=random.randint(1, 100),
                weight=random.randint(100, 5000),  # Weight in kg
                volume=random.randint(1, 100),  # Volume in cubic meters
                pack_type_id=random.choice(packtypes).id,
                commodity_id=random.choice(commodities).id,
                container_id=random.choice(containers).id,
                manifester_id=manifest.manifester_id  # Use same manifester as the manifest
            )
            db_session.add(line_item)
    db_session.commit()

    # Create container history entries
    damage_descriptions = [
        "Minor dent on side panel",
        "Scratches on door",
        "Corner damage",
        "Rust spots",
        "Door seal damaged",
        "Floor damage",
        "Roof puncture",
        "Paint damage",
        None  # No damage
    ]

    # Create 2-5 history entries for each container
    for container in containers:
        num_entries = random.randint(2, 5)
        # Sort dates to ensure chronological order
        dates = sorted([datetime.now() - timedelta(days=random.randint(0, 365)) 
                       for _ in range(num_entries)])
        
        for date in dates:
            history = ContainerHistory(
                container_id=container.id,
                port_id=random.choice(ports).id,
                client_id=random.choice(clients).id,
                container_status_id=random.choice(container_statuses).id,
                damage=random.choice(damage_descriptions),
                updated=date
            )
            db_session.add(history)
    db_session.commit()

    # Create test rates
    # Create rates for each combination of commodity, pack type, and client
    start_date = datetime(2024, 1, 1)
    for commodity in commodities:
        for packtype in packtypes:
            for client in clients:
                # Create 1-3 rates with different distances
                for _ in range(random.randint(1, 3)):
                    distance = random.randint(500, 10000)  # Distance in nautical miles
                    # Rate per unit (higher for valuable commodities, special packaging)
                    base_rate = random.uniform(50, 500)
                    
                    # Adjust rate based on commodity (electronics more expensive than raw materials)
                    commodity_factor = 1.0
                    if "Electronics" in commodity.name:
                        commodity_factor = 2.0
                    elif "Medical" in commodity.name:
                        commodity_factor = 1.8
                    elif "Raw Materials" in commodity.name:
                        commodity_factor = 0.8
                    
                    # Adjust rate based on pack type (special packaging costs more)
                    packtype_factor = 1.0
                    if packtype.name in ["Case", "Crate"]:
                        packtype_factor = 1.3
                    elif packtype.name == "Loose":
                        packtype_factor = 0.7
                    
                    final_rate = base_rate * commodity_factor * packtype_factor
                    
                    # Random effective date within 2024
                    effective_date = start_date + timedelta(days=random.randint(0, 364))
                    
                    rate = Rate(
                        distance=distance,
                        commodity_id=commodity.id,
                        pack_type_id=packtype.id,
                        client_id=client.id,
                        rate=round(final_rate, 2),
                        effective=effective_date
                    )
                    db_session.add(rate)
    db_session.commit()

    print("Test data initialized successfully.")

if __name__ == "__main__":
    init_test_data()
