from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional
import numpy as np
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from config import Config
from generated_models.client import Client
from generated_models.commodity import Commodity
from generated_models.container import Container
from generated_models.manifest import Manifest
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from generated_models.port import Port
from generated_models.country import Country
from generated_models.shippingcompany import ShippingCompany
from generated_models.lineitem import LineItem
from generated_models.packtype import PackType
from generated_models.containerstatus import ContainerStatus
from generated_models.user import User
from helper_functions import get_commodity_data, get_packtype_data

class DataGenerationConfig:
    def __init__(self):
        self.num_clients = 300
        self.num_commodities = 50
        self.num_containers = 1000
        self.num_vessels = 20
        self.num_voyages = 100
        self.num_manifests = 500
        self.batch_size = 100
        self.num_threads = 4
        self.include_edge_cases = True
        self.seasonal_patterns = True
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2024, 12, 31)

class DataGenerator:
    def __init__(self, config: DataGenerationConfig):
        self.config = config
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.validation_errors = []
        
        # Seasonal patterns (monthly factors)
        self.seasonal_factors = {
            1: 0.8,  # January - Lower volume
            2: 0.7,  # February
            3: 0.9,  # March - Spring increase
            4: 1.0,  # April
            5: 1.1,  # May
            6: 1.2,  # June - Summer peak
            7: 1.3,  # July
            8: 1.4,  # August - Peak season
            9: 1.3,  # September
            10: 1.1, # October
            11: 1.0, # November
            12: 1.2  # December - Holiday season
        }

    def generate_all(self):
        """Main method to generate all test data"""
        try:
            with Session(self.engine) as session:
                print("Generating test data...")
                
                # Generate countries first
                countries = self._generate_countries(session)
                print("Generated countries")
                
                # Generate ports
                ports = self._generate_ports(session, countries)
                print("Generated ports")
                
                # Generate container statuses
                statuses = self._generate_container_statuses(session)
                print("Generated container statuses")
                
                # Generate base data
                clients = self._generate_clients(session, countries)
                print("Generated clients")
                
                commodities = self._generate_commodities(session)
                print("Generated commodities")
                
                packtypes = self._generate_packtypes(session)
                print("Generated pack types")
                
                containers = self._generate_containers(session, ports, statuses)
                print("Generated containers")
                
                # Generate shipping companies before vessels
                shipping_companies = self._generate_shipping_companies(session)
                print("Generated shipping companies")
                
                vessels = self._generate_vessels(session, shipping_companies)
                print("Generated vessels")
                
                # Generate voyages with seasonal patterns
                voyages = self._generate_voyages(session, vessels)
                print("Generated voyages")
                
                # Generate users before manifests
                users = self._generate_users(session)
                print("Generated users")
                
                # Generate manifests and line items in parallel
                manifests = self._generate_manifests_parallel(
                    session, clients, voyages, ports, users, commodities, packtypes
                )
                print("Generated manifests")
                
                # Generate edge cases if configured
                if self.config.include_edge_cases:
                    self._generate_edge_cases(
                        session, clients, voyages, ports, users, commodities, packtypes
                    )
                    print("Generated edge cases")
                
                # Validate generated data
                self._validate_data(session)
                if self.validation_errors:
                    print("\nValidation errors found:")
                    for error in self.validation_errors:
                        print(f"- {error}")
                else:
                    print("All data validated successfully")
                
                return {
                    'clients': clients,
                    'commodities': commodities,
                    'containers': containers,
                    'vessels': vessels,
                    'voyages': voyages,
                    'manifests': manifests
                }
        except Exception as e:
            print(f"Error generating data: {str(e)}")
            raise

    def _generate_countries(self, session: Session) -> List[Country]:
        """Generate country data"""
        countries = []
        country_names = [
            "United States",
            "United Kingdom",
            "China",
            "Japan",
            "Germany",
            "France",
            "Italy",
            "Canada",
            "Australia",
            "Brazil"
        ]
        
        for name in country_names:
            country = Country(name=name)
            countries.append(country)
            session.add(country)
        
        session.commit()
        return countries

    def _generate_ports(self, session: Session, countries: List[Country]) -> List[Port]:
        """Generate port data"""
        ports = []
        port_data = [
            ("Los Angeles", "United States", "LAX"),
            ("Long Beach", "United States", "LGB"),
            ("New York", "United States", "NYC"),
            ("Shanghai", "China", "SHA"),
            ("Hong Kong", "China", "HKG"),
            ("Tokyo", "Japan", "TYO"),
            ("Hamburg", "Germany", "HAM"),
            ("London", "United Kingdom", "LON"),
            ("Sydney", "Australia", "SYD"),
            ("Vancouver", "Canada", "YVR")
        ]
        
        country_map = {country.name: country for country in countries}
        
        for name, country_name, prefix in port_data:
            country = country_map[country_name]
            port = Port(
                name=name,
                country_id=country.id,
                prefix=prefix
            )
            ports.append(port)
            session.add(port)
        
        session.commit()
        return ports

    def _generate_container_statuses(self, session: Session) -> List[ContainerStatus]:
        """Generate container status data"""
        statuses = []
        status_data = [
            ("Available", "Container is available for booking"),
            ("In Use", "Container is currently in use"),
            ("Maintenance", "Container is under maintenance"),
            ("Damaged", "Container is damaged and needs repair"),
            ("Reserved", "Container is reserved for future booking")
        ]
        
        for name, description in status_data:
            status = ContainerStatus(
                name=name,
                description=description
            )
            statuses.append(status)
            session.add(status)
        
        session.commit()
        return statuses

    def _generate_shipping_companies(self, session: Session) -> List[ShippingCompany]:
        """Generate shipping company data"""
        companies = []
        company_data = [
            "Maersk Line",
            "MSC",
            "CMA CGM",
            "COSCO",
            "Hapag-Lloyd",
            "ONE",
            "Evergreen",
            "Yang Ming",
            "HMM",
            "PIL"
        ]
        
        for name in company_data:
            company = ShippingCompany(name=name)
            companies.append(company)
            session.add(company)
        
        session.commit()
        return companies

    def _generate_clients(self, session: Session, countries: List[Country]) -> List[Client]:
        """Generate client data with realistic patterns"""
        clients = []
        company_types = ['LLC', 'Inc.', 'Corp', 'Ltd']
        cities = ['New York', 'London', 'Shanghai', 'Tokyo', 'Berlin', 'Paris']
        
        for i in range(self.config.num_clients):
            country = random.choice(countries)
            city = random.choice(cities)
            company_name = f"Company{i} {random.choice(company_types)}"
            contact_name = f"Contact {i}"
            
            client = Client(
                name=company_name,
                email=f"contact@{company_name.lower().replace(' ', '')}.com",
                address=f"{random.randint(1, 999)} Business Ave, Suite {random.randint(100, 999)}",
                town=city,
                country_id=country.id,
                contact_person=contact_name,
                phone=f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            )
            clients.append(client)
            session.add(client)
            
            if len(clients) % self.config.batch_size == 0:
                session.commit()
        
        session.commit()
        return clients

    def _generate_commodities(self, session: Session) -> List[Commodity]:
        """Generate commodity data with industry-specific patterns"""
        commodities = []
        used_names = set()
        
        while len(commodities) < self.config.num_commodities:
            name, description = get_commodity_data()
            if name not in used_names:
                used_names.add(name)
                commodity = Commodity(
                    name=name,
                    description=description
                )
                commodities.append(commodity)
                session.add(commodity)
        
        session.commit()
        return commodities

    def _generate_packtypes(self, session: Session) -> List[PackType]:
        """Generate pack type data"""
        packtypes = []
        
        for name, description in get_packtype_data():
            packtype = PackType(
                name=name,
                description=description
            )
            packtypes.append(packtype)
            session.add(packtype)
        
        session.commit()
        return packtypes

    def _generate_containers(
        self,
        session: Session,
        ports: List[Port],
        statuses: List[ContainerStatus]
    ) -> List[Container]:
        """Generate container data with realistic specifications"""
        containers = []
        container_types = ['DRY', 'REEF', 'TANK', 'FLAT', 'OPEN']
        sizes = ['20', '40', '45']
        
        for i in range(self.config.num_containers):
            size = np.random.choice(sizes, p=[0.4, 0.5, 0.1])  # Realistic size distribution
            container_type = np.random.choice(container_types, p=[0.6, 0.2, 0.1, 0.05, 0.05])
            
            container = Container(
                container_number=f"{random.choice(['MAEU', 'CMAU', 'OOLU'])}{random.randint(100000, 999999)}",
                container_type=container_type,
                size=size,
                max_weight=20000.0 if size == '20' else 30000.0,
                port_id=random.choice(ports).id,
                status_id=random.choice(statuses).id,
                updated=self._random_date(
                    datetime(2023, 1, 1),
                    datetime(2024, 12, 31)
                )
            )
            containers.append(container)
            session.add(container)
            
            if len(containers) % self.config.batch_size == 0:
                session.commit()
        
        session.commit()
        return containers

    def _generate_vessels(
        self,
        session: Session,
        shipping_companies: List[ShippingCompany]
    ) -> List[Vessel]:
        """Generate vessel data with realistic specifications"""
        vessels = []
        vessel_names = [
            "Ocean Pioneer", "Pacific Voyager", "Atlantic Carrier",
            "Global Express", "Sea Navigator", "Maritime Leader"
        ]
        
        for i in range(self.config.num_vessels):
            vessel = Vessel(
                name=f"{random.choice(vessel_names)} {random.randint(1, 100)}",
                shipping_company_id=random.choice(shipping_companies).id
            )
            vessels.append(vessel)
            session.add(vessel)
        
        session.commit()
        return vessels

    def _generate_voyages(self, session: Session, vessels: List[Vessel]) -> List[Voyage]:
        """Generate voyage data with seasonal patterns"""
        voyages = []
        current_date = self.config.start_date
        
        while current_date <= self.config.end_date:
            # Apply seasonal factor to number of voyages
            month_factor = self.seasonal_factors[current_date.month]
            num_voyages_this_month = int(
                self.config.num_voyages / 24 * month_factor  # 24 months total
            )
            
            for _ in range(num_voyages_this_month):
                vessel = random.choice(vessels)
                duration = timedelta(days=random.randint(14, 45))
                
                voyage = Voyage(
                    voyage_number=f"V{current_date.year}{current_date.month:02d}{random.randint(100, 999)}",
                    vessel_id=vessel.id,
                    departure_date=current_date,
                    arrival_date=current_date + duration,
                    rotation_number=f"ROT{random.randint(1000, 9999)}"
                )
                voyages.append(voyage)
                session.add(voyage)
            
            current_date += timedelta(days=30)  # Move to next month
            session.commit()
        
        return voyages

    def _generate_users(self, session: Session) -> List[User]:
        """Generate user data"""
        users = []
        for i in range(10):  # Generate 10 users
            user = User(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password_hash="hashed_password"  # In real system, would use proper hashing
            )
            users.append(user)
            session.add(user)
        
        session.commit()
        return users

    def _generate_manifests_parallel(
        self,
        session: Session,
        clients: List[Client],
        voyages: List[Voyage],
        ports: List[Port],
        users: List[User],
        commodities: List[Commodity],
        packtypes: List[PackType]
    ) -> List[Manifest]:
        """Generate manifests and line items using parallel processing"""
        manifests = []
        
        def create_manifest_batch(batch_size: int) -> List[Manifest]:
            with Session(self.engine) as batch_session:
                batch_manifests = []
                for _ in range(batch_size):
                    try:
                        manifest = self._create_single_manifest(
                            batch_session,
                            random.choice(clients),
                            random.choice(voyages),
                            random.choice(ports),
                            random.choice(users),
                            commodities,
                            packtypes
                        )
                        if manifest:
                            batch_manifests.append(manifest)
                    except Exception as e:
                        print(f"Error creating manifest: {str(e)}")
                        continue
                
                try:
                    batch_session.commit()
                except Exception as e:
                    print(f"Error committing batch: {str(e)}")
                    batch_session.rollback()
                
                return batch_manifests
        
        # Split work into batches for parallel processing
        batch_sizes = [
            self.config.batch_size
            for _ in range(self.config.num_manifests // self.config.batch_size)
        ]
        if self.config.num_manifests % self.config.batch_size:
            batch_sizes.append(
                self.config.num_manifests % self.config.batch_size
            )
        
        # Execute batches in parallel
        with ThreadPoolExecutor(max_workers=self.config.num_threads) as executor:
            future_to_batch = {
                executor.submit(create_manifest_batch, size): size
                for size in batch_sizes
            }
            
            for future in as_completed(future_to_batch):
                try:
                    batch_manifests = future.result()
                    manifests.extend(batch_manifests)
                except Exception as e:
                    print(f"Error in manifest batch: {str(e)}")
        
        return manifests

    def _create_single_manifest(
        self,
        session: Session,
        client: Client,
        voyage: Voyage,
        port: Port,
        user: User,
        commodities: List[Commodity],
        packtypes: List[PackType]
    ) -> Optional[Manifest]:
        """Create a single manifest with associated line items"""
        try:
            manifest = Manifest(
                bill_of_lading=f"BL{random.randint(100000, 999999)}",
                shipper_id=client.id,
                consignee_id=client.id,  # Using same client as shipper and consignee for simplicity
                vessel_id=voyage.vessel_id,
                voyage_id=voyage.id,
                port_of_loading_id=port.id,
                port_of_discharge_id=port.id,  # Using same port for loading and discharge for simplicity
                place_of_delivery=f"Warehouse {random.randint(1, 100)}",
                place_of_receipt=f"Factory {random.randint(1, 100)}",
                clauses="Standard shipping terms apply",
                date_of_receipt=self._random_date(
                    voyage.departure_date - timedelta(days=30),
                    voyage.departure_date - timedelta(days=1)
                ),
                manifester_id=user.id
            )
            session.add(manifest)
            session.flush()  # Get manifest ID
            
            # Generate line items
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                self._create_line_item(session, manifest, commodities, packtypes)
            
            return manifest
        except Exception as e:
            print(f"Error creating manifest: {str(e)}")
            session.rollback()
            return None

    def _create_line_item(
        self,
        session: Session,
        manifest: Manifest,
        commodities: List[Commodity],
        packtypes: List[PackType]
    ):
        """Create a single line item with realistic specifications"""
        try:
            packtype = random.choice(packtypes)
            commodity = random.choice(commodities)
            
            # Apply seasonal factor to quantity
            base_quantity = random.randint(1, 100)
            seasonal_factor = self.seasonal_factors[manifest.date_of_receipt.month]
            adjusted_quantity = int(base_quantity * seasonal_factor)
            
            line_item = LineItem(
                manifest_id=manifest.id,
                commodity_id=commodity.id,
                pack_type_id=packtype.id,
                quantity=adjusted_quantity,
                weight=random.randint(100, 5000),
                volume=random.randint(10, 500),
                description=f"{commodity.name} - {packtype.name}"
            )
            session.add(line_item)
        except Exception as e:
            print(f"Error creating line item: {str(e)}")
            raise

    def _generate_edge_cases(
        self,
        session: Session,
        clients: List[Client],
        voyages: List[Voyage],
        ports: List[Port],
        users: List[User],
        commodities: List[Commodity],
        packtypes: List[PackType]
    ):
        """Generate edge cases for testing boundary conditions"""
        try:
            # Maximum weight manifest
            max_weight_manifest = Manifest(
                bill_of_lading="MAXWEIGHT001",
                shipper_id=clients[0].id,
                consignee_id=clients[0].id,
                vessel_id=voyages[0].vessel_id,
                voyage_id=voyages[0].id,
                port_of_loading_id=ports[0].id,
                port_of_discharge_id=ports[0].id,
                place_of_delivery="Max Weight Test Warehouse",
                place_of_receipt="Max Weight Test Factory",
                clauses="Test case for maximum weight",
                date_of_receipt=voyages[0].departure_date - timedelta(days=7),
                manifester_id=users[0].id
            )
            session.add(max_weight_manifest)
            session.flush()
            
            # Add maximum weight line items
            line_item = LineItem(
                manifest_id=max_weight_manifest.id,
                commodity_id=commodities[0].id,
                pack_type_id=packtypes[0].id,
                quantity=1,
                weight=20000,  # Maximum container weight
                volume=100
            )
            session.add(line_item)
            
            # Zero quantity manifest
            zero_manifest = Manifest(
                bill_of_lading="ZERO001",
                shipper_id=clients[0].id,
                consignee_id=clients[0].id,
                vessel_id=voyages[0].vessel_id,
                voyage_id=voyages[0].id,
                port_of_loading_id=ports[0].id,
                port_of_discharge_id=ports[0].id,
                place_of_delivery="Zero Quantity Test Warehouse",
                place_of_receipt="Zero Quantity Test Factory",
                clauses="Test case for zero quantity",
                date_of_receipt=voyages[0].departure_date - timedelta(days=7),
                manifester_id=users[0].id
            )
            session.add(zero_manifest)
            session.flush()
            
            line_item = LineItem(
                manifest_id=zero_manifest.id,
                commodity_id=commodities[0].id,
                pack_type_id=packtypes[0].id,
                quantity=0,
                weight=0,
                volume=0
            )
            session.add(line_item)
            
            session.commit()
        except Exception as e:
            print(f"Error generating edge cases: {str(e)}")
            session.rollback()

    def _validate_data(self, session: Session):
        """Validate generated data for consistency and referential integrity"""
        try:
            # Check for manifests without line items
            orphan_manifests = session.query(Manifest)\
                .outerjoin(LineItem)\
                .group_by(Manifest.id)\
                .having(func.count(LineItem.id) == 0)\
                .all()
            if orphan_manifests:
                self.validation_errors.append(
                    f"Found {len(orphan_manifests)} manifests without line items"
                )
            
            # Check for container weight limits
            overweight_manifests = session.query(func.sum(LineItem.weight).label('total_weight'), Manifest)\
                .select_from(Manifest)\
                .join(LineItem)\
                .group_by(Manifest.id)\
                .having(func.sum(LineItem.weight) > 30000)\
                .all()
            if overweight_manifests:
                self.validation_errors.append(
                    f"Found {len(overweight_manifests)} overweight manifests"
                )
            
            # Check date consistency
            invalid_dates = session.query(Manifest)\
                .join(Voyage)\
                .filter(Manifest.date_of_receipt > Voyage.departure_date)\
                .all()
            if invalid_dates:
                self.validation_errors.append(
                    f"Found {len(invalid_dates)} manifests with invalid dates"
                )
        except Exception as e:
            print(f"Error validating data: {str(e)}")

    def _random_date(self, start_date: datetime, end_date: datetime) -> datetime:
        """Generate a random date between start_date and end_date"""
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randint(0, days_between)
        return start_date + timedelta(days=random_days)

if __name__ == '__main__':
    config = DataGenerationConfig()
    generator = DataGenerator(config)
    generator.generate_all()
