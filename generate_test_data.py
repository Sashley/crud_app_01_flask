from datetime import datetime, timedelta
import random
from database import db_session
from generated_models.manifest import Manifest
from generated_models.lineitem import LineItem
from generated_models.client import Client
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from generated_models.port import Port
from generated_models.user import User
from generated_models.packtype import PackType
from generated_models.commodity import Commodity
from generated_models.container import Container

def get_random_record(model):
    """Get a random record from a model"""
    return random.choice(db_session.query(model).all())

def generate_bill_of_lading():
    """Generate a random bill of lading number"""
    prefix = random.choice(['MAEU', 'MSCU', 'OOLU', 'CMAU', 'HLCU'])
    number = ''.join(random.choices('0123456789', k=7))
    return f"{prefix}{number}"

def generate_description():
    """Generate a random cargo description"""
    adjectives = ['NEW', 'USED', 'FRESH', 'FROZEN', 'DRIED', 'PROCESSED']
    items = ['ELECTRONICS', 'TEXTILES', 'MACHINERY', 'FURNITURE', 'FOOD PRODUCTS', 'AUTO PARTS']
    return f"{random.choice(adjectives)} {random.choice(items)}"

def create_test_data():
    try:
        # Create 5000 manifests
        total_manifests = 5000
        print(f"Creating {total_manifests} manifests...")
        for i in range(total_manifests):
            # Create manifest
            manifest = Manifest(
                bill_of_lading=generate_bill_of_lading(),
                shipper_id=get_random_record(Client).id,
                consignee_id=get_random_record(Client).id,
                vessel_id=get_random_record(Vessel).id,
                voyage_id=get_random_record(Voyage).id,
                port_of_loading_id=get_random_record(Port).id,
                port_of_discharge_id=get_random_record(Port).id,
                place_of_delivery=random.choice(['WAREHOUSE A', 'TERMINAL B', 'DEPOT C', 'FACILITY D']),
                place_of_receipt=random.choice(['FACTORY X', 'PLANT Y', 'STORAGE Z']),
                clauses=None,
                date_of_receipt=datetime.now() - timedelta(days=random.randint(0, 365)),
                manifester_id=get_random_record(User).id
            )
            db_session.add(manifest)
            db_session.flush()  # Get the manifest ID

            # Create 1-4 line items for each manifest
            num_line_items = random.randint(1, 4)
            for j in range(num_line_items):
                line_item = LineItem(
                    manifest_id=manifest.id,
                    description=generate_description(),
                    quantity=random.randint(1, 1000),
                    weight=random.randint(100, 50000),
                    volume=random.randint(1, 100),
                    pack_type_id=get_random_record(PackType).id,
                    commodity_id=get_random_record(Commodity).id,
                    container_id=get_random_record(Container).id,
                    manifester_id=manifest.manifester_id
                )
                db_session.add(line_item)

            # Commit every 100 manifests to avoid memory issues
            if (i + 1) % 100 == 0:
                progress = (i + 1) / total_manifests * 100
                print(f"Progress: {progress:.1f}% ({i + 1} manifests created)")
                db_session.commit()

        # Final commit
        db_session.commit()
        print(f"Successfully created {total_manifests} manifests with line items!")

    except Exception as e:
        print(f"Error creating test data: {str(e)}")
        db_session.rollback()
    finally:
        db_session.close()

if __name__ == '__main__':
    create_test_data()
