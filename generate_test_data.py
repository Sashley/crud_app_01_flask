#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from faker import Faker
from datetime import datetime, timedelta, date
import random
from database import db_session
from generated_models.country import Country
from generated_models.port import Port
from generated_models.client import Client
from generated_models.user import User
from generated_models.vessel import Vessel
from generated_models.shippingcompany import ShippingCompany
from generated_models.voyage import Voyage
from generated_models.container import Container
from generated_models.containerstatus import ContainerStatus
from generated_models.containerhistory import ContainerHistory
from generated_models.manifest import Manifest
from generated_models.lineitem import LineItem
from generated_models.commodity import Commodity
from generated_models.packtype import PackType
from generated_models.portpair import PortPair
from generated_models.rate import Rate
from generated_models.leg import Leg
from sqlalchemy.exc import SQLAlchemyError
from app import app
from helper_functions import get_commodity_data, get_packtype_data

fake = Faker()

def generate_test_data():
    try:
        with app.app_context():
            # Clear existing data
            db_session.query(LineItem).delete()
            db_session.query(Manifest).delete()
            db_session.query(ContainerHistory).delete()
            db_session.query(Container).delete()
            db_session.query(ContainerStatus).delete()
            db_session.query(Rate).delete()
            db_session.query(PortPair).delete()
            db_session.query(PackType).delete()
            db_session.query(Commodity).delete()
            db_session.query(Leg).delete()
            db_session.query(Voyage).delete()
            db_session.query(Vessel).delete()
            db_session.query(ShippingCompany).delete()
            db_session.query(Port).delete()
            db_session.query(Client).delete()
            db_session.query(Country).delete()
            db_session.query(User).delete()
            db_session.commit()

            print("Generating test data...")

            # Generate countries
            countries = [
                Country(name="United States", code="US", region="North America"),
                Country(name="United Kingdom", code="GB", region="Europe"),
                Country(name="China", code="CN", region="Asia"),
                Country(name="Japan", code="JP", region="Asia"),
                Country(name="Germany", code="DE", region="Europe"),
                Country(name="France", code="FR", region="Europe"),
                Country(name="Italy", code="IT", region="Europe"),
                Country(name="Canada", code="CA", region="North America"),
                Country(name="Australia", code="AU", region="Oceania"),
                Country(name="Brazil", code="BR", region="South America")
            ]
            for country in countries:
                db_session.add(country)
            db_session.commit()
            print("Generated countries")

            # Generate ports
            ports = []
            port_data = [
                ("Los Angeles", "US", "LAX"),
                ("Long Beach", "US", "LGB"),
                ("New York", "US", "NYC"),
                ("Shanghai", "CN", "SHA"),
                ("Hong Kong", "CN", "HKG"),
                ("Tokyo", "JP", "TYO"),
                ("Hamburg", "DE", "HAM"),
                ("London", "GB", "LON"),
                ("Sydney", "AU", "SYD"),
                ("Vancouver", "CA", "YVR")
            ]
            
            for name, country_code, prefix in port_data:
                country = next(c for c in countries if c.code == country_code)
                port = Port(name=name, country_id=country.id, prefix=prefix)
                ports.append(port)
                db_session.add(port)
            db_session.commit()
            print("Generated ports")

            # Generate port pairs with distance codes
            # For each port, create a pair with every other port
            for pol in ports:
                for pod in ports:
                    if pol != pod:  # Don't create pairs for same port
                        # Calculate a mock distance (this would be real distance in production)
                        mock_distance = random.randint(100, 10000)
                        # Assign distance code based on distance ranges
                        if mock_distance <= 500:
                            distance_code = 1
                        elif mock_distance <= 1000:
                            distance_code = 2
                        elif mock_distance <= 2000:
                            distance_code = 3
                        elif mock_distance <= 3000:
                            distance_code = 4
                        elif mock_distance <= 4000:
                            distance_code = 5
                        elif mock_distance <= 6000:
                            distance_code = 6
                        elif mock_distance <= 8000:
                            distance_code = 7
                        else:
                            distance_code = 8
                        
                        port_pair = PortPair(
                            pol_id=pol.id,
                            pod_id=pod.id,
                            distance=mock_distance,
                            distance_code=distance_code
                        )
                        db_session.add(port_pair)
            db_session.commit()
            print("Generated port pairs")

            # Generate container statuses (at least 20)
            status_data = [
                ("Available", "Container is available for booking"),
                ("In Use", "Container is currently in use"),
                ("Maintenance", "Container is under maintenance"),
                ("Damaged", "Container is damaged and needs repair"),
                ("Reserved", "Container is reserved for future booking"),
                ("In Transit", "Container is in transit"),
                ("At Terminal", "Container is at terminal"),
                ("Loading", "Container is being loaded"),
                ("Unloading", "Container is being unloaded"),
                ("Customs Hold", "Container is held by customs"),
                ("Inspection", "Container is under inspection"),
                ("Cleaning", "Container is being cleaned"),
                ("Repair", "Container is under repair"),
                ("Storage", "Container is in storage"),
                ("Empty", "Container is empty"),
                ("Full", "Container is full"),
                ("Booking Confirmed", "Container booking is confirmed"),
                ("Ready for Pickup", "Container is ready for pickup"),
                ("Delivered", "Container has been delivered"),
                ("Returned", "Container has been returned")
            ]
            
            statuses = []
            for name, description in status_data:
                status = ContainerStatus(name=name, description=description)
                statuses.append(status)
                db_session.add(status)
            db_session.commit()
            print("Generated container statuses")

            # Generate clients (100)
            clients = []
            for _ in range(100):
                country = random.choice(countries)
                client = Client(
                    name=fake.company(),
                    address=fake.street_address(),
                    town=fake.city(),
                    country_id=country.id,
                    contact_person=fake.name(),
                    email=fake.company_email(),
                    phone=fake.phone_number()
                )
                clients.append(client)
                db_session.add(client)
            db_session.commit()
            print("Generated clients")

            # Generate commodities (at least 30)
            commodities = []
            commodity_names = [
                "Electronics", "Textiles", "Machinery", "Chemicals", "Food Products",
                "Automotive Parts", "Pharmaceuticals", "Raw Materials", "Construction Materials", "Medical Supplies",
                "Furniture", "Paper Products", "Metal Products", "Plastic Products", "Agricultural Products",
                "Consumer Goods", "Industrial Equipment", "Steel Products", "Wood Products", "Glass Products",
                "Rubber Products", "Leather Goods", "Sports Equipment", "Office Supplies", "Home Appliances",
                "Toys", "Books", "Art Supplies", "Musical Instruments", "Pet Supplies"
            ]
            for name in commodity_names:
                commodity = Commodity(
                    name=name,
                    description=f"Various {name.lower()} and related items"
                )
                commodities.append(commodity)
                db_session.add(commodity)
            db_session.commit()
            print("Generated commodities")

            # Generate pack types
            packtypes = []
            packtype_data = [
                ("Loose", "Loose cargo without specific packaging"),
                ("Palletized", "Cargo secured on pallets"),
                ("Boxed", "Cargo in boxes"),
                ("Drums", "Cargo in drums"),
                ("Bags", "Cargo in bags"),
                ("Crates", "Cargo in crates"),
                ("Bundles", "Cargo in bundles"),
                ("Rolls", "Cargo in rolls")
            ]
            for name, description in packtype_data:
                packtype = PackType(name=name, description=description)
                packtypes.append(packtype)
                db_session.add(packtype)
            db_session.commit()
            print("Generated pack types")

            # Generate rates for each distance code and pack type combination
            for distance_code in range(1, 9):  # 8 distance codes
                for packtype in packtypes:
                    for commodity in commodities:
                        rate = Rate(
                            distance_code=distance_code,
                            commodity_id=commodity.id,
                            pack_type_id=packtype.id,
                            client_id=None,  # No customer-specific rates
                            rate=random.uniform(100, 1000) * distance_code,
                            effective=datetime.now()
                        )
                        db_session.add(rate)
            db_session.commit()
            print("Generated rates")

            # Generate containers (500)
            containers = []
            container_types = ['20GP', '40GP', '40HC', '20RF', '40RF']
            sizes = ['20', '40', '45']
            max_weights = {'20': 28000, '40': 32500, '45': 32500}
            
            for _ in range(500):
                size = random.choice(sizes)
                container_type = random.choice(container_types)
                container = Container(
                    container_number=f"{random.choice(['MAEU', 'CMAU', 'OOLU'])}{random.randint(100000, 999999)}",
                    container_type=container_type,
                    size=size,
                    max_weight=max_weights[size],
                    port_id=random.choice(ports).id,
                    status_id=random.choice(statuses).id,
                    updated=datetime.now()
                )
                containers.append(container)
                db_session.add(container)
            db_session.commit()
            print("Generated containers")

            # Generate container history (at least 5 per container)
            for container in containers:
                # Generate between 5 and 10 history records for each container
                num_records = random.randint(5, 10)
                for i in range(num_records):
                    history = ContainerHistory(
                        container_id=container.id,
                        port_id=random.choice(ports).id,
                        client_id=random.choice(clients).id,
                        container_status_id=random.choice(statuses).id,
                        damage=fake.text(max_nb_chars=50) if random.random() < 0.2 else None,
                        updated=datetime.now() - timedelta(days=i*30)
                    )
                    db_session.add(history)
            db_session.commit()
            print("Generated container histories")

            # Generate shipping companies
            companies = []
            company_names = [
                "Maersk Line", "MSC", "CMA CGM", "COSCO", "Hapag-Lloyd",
                "ONE", "Evergreen", "Yang Ming", "HMM", "PIL"
            ]
            for name in company_names:
                company = ShippingCompany(name=name)
                companies.append(company)
                db_session.add(company)
            db_session.commit()
            print("Generated shipping companies")

            # Generate vessels (50)
            vessels = []
            vessel_names = [
                "Ocean Pioneer", "Pacific Voyager", "Atlantic Carrier",
                "Global Express", "Sea Navigator", "Maritime Leader"
            ]
            for _ in range(50):
                vessel = Vessel(
                    name=f"{random.choice(vessel_names)} {random.randint(1, 100)}",
                    shipping_company_id=random.choice(companies).id
                )
                vessels.append(vessel)
                db_session.add(vessel)
            db_session.commit()
            print("Generated vessels")

            # Generate voyages (200)
            voyages = []
            start_date = date(2023, 1, 1)
            for _ in range(200):
                vessel = random.choice(vessels)
                departure_date = start_date + timedelta(days=random.randint(0, 365))
                arrival_date = departure_date + timedelta(days=random.randint(14, 45))
                voyage = Voyage(
                    voyage_number=f"V{departure_date.strftime('%y%m')}{random.randint(100, 999)}",
                    vessel_id=vessel.id,
                    departure_date=departure_date,
                    arrival_date=arrival_date,
                    rotation_number=random.randint(1000, 9999)
                )
                voyages.append(voyage)
                db_session.add(voyage)
            db_session.commit()
            print("Generated voyages")

            # Generate legs for each voyage
            for voyage in voyages:
                voyage_ports = random.sample(ports, random.randint(2, 5))
                for i, port in enumerate(voyage_ports):
                    eta = datetime.now() + timedelta(days=i*7)
                    etd = eta + timedelta(days=1)
                    leg = Leg(
                        voyage_id=voyage.id,
                        port_id=port.id,
                        leg_number=i+1,
                        eta=eta,
                        etd=etd
                    )
                    db_session.add(leg)
            db_session.commit()
            print("Generated voyage legs")

            # Generate users (10)
            users = []
            for i in range(10):
                user = User(
                    name=fake.name(),
                    email=fake.email(),
                    password_hash="pbkdf2:sha256:dummy_hash"  # In real system, would use proper hashing
                )
                users.append(user)
                db_session.add(user)
            db_session.commit()
            print("Generated users")

            # Generate manifests (300)
            manifests = []
            for _ in range(300):
                manifest = Manifest(
                    bill_of_lading=f"BL{random.randint(100000, 999999)}",
                    shipper_id=random.choice(clients).id,
                    consignee_id=random.choice(clients).id,
                    vessel_id=random.choice(vessels).id,
                    voyage_id=random.choice(voyages).id,
                    port_of_loading_id=random.choice(ports).id,
                    port_of_discharge_id=random.choice(ports).id,
                    place_of_delivery=fake.street_address(),
                    place_of_receipt=fake.street_address(),
                    clauses="Standard shipping terms apply",
                    date_of_receipt=datetime.now(),
                    manifester_id=random.choice(users).id
                )
                manifests.append(manifest)
                db_session.add(manifest)
            db_session.commit()
            print("Generated manifests")

            # Generate line items for manifests
            for manifest in manifests:
                for _ in range(random.randint(1, 5)):
                    line_item = LineItem(
                        manifest_id=manifest.id,
                        description=fake.text(max_nb_chars=100),
                        quantity=random.randint(1, 1000),
                        weight=random.randint(100, 5000),
                        volume=random.randint(1, 100),
                        pack_type_id=random.choice(packtypes).id,
                        commodity_id=random.choice(commodities).id,
                        container_id=random.choice(containers).id,
                        manifester_id=random.choice(users).id
                    )
                    db_session.add(line_item)
            db_session.commit()
            print("Generated line items")

            print("Successfully generated all test data")

    except Exception as e:
        print(f"Error generating test data: {str(e)}")
        db_session.rollback()
        raise

if __name__ == "__main__":
    generate_test_data()
