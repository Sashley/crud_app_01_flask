from app import app
from database import db_session
from generated_models.manifest import Manifest
from generated_models.client import Client
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from bs4 import BeautifulSoup
from sqlalchemy import select
import logging

logging.basicConfig(level=logging.DEBUG)

def test_foreign_key_names():
    print("\nTesting foreign key name replacements in manifest list...")
    
    with app.test_client() as client:
        # First, get a specific manifest with known relationships
        stmt = select(Manifest).limit(1)
        manifest = db_session.scalar(stmt)
        
        # Get the related records using SQLAlchemy 2.0 style
        shipper = db_session.scalar(select(Client).where(Client.id == manifest.shipper_id))
        consignee = db_session.scalar(select(Client).where(Client.id == manifest.consignee_id))
        vessel = db_session.scalar(select(Vessel).where(Vessel.id == manifest.vessel_id))
        voyage = db_session.scalar(select(Voyage).where(Voyage.id == manifest.voyage_id))
        
        print(f"\nChecking manifest {manifest.bill_of_lading}:")
        print(f"Expected relationships:")
        print(f"  Shipper ID: {manifest.shipper_id} -> Name: {shipper.name}")
        print(f"  Consignee ID: {manifest.consignee_id} -> Name: {consignee.name}")
        print(f"  Vessel ID: {manifest.vessel_id} -> Name: {vessel.name}")
        print(f"  Voyage ID: {manifest.voyage_id} -> Name: {voyage.name}")
        
        # Get the list view
        response = client.get('/manifest')
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.data.decode(), 'html.parser')
            
            # Find the row for our manifest
            rows = soup.find_all('tr')
            manifest_row = None
            for row in rows[1:]:  # Skip header row
                cols = row.find_all('td')
                if cols and cols[0].text.strip() == manifest.bill_of_lading:
                    manifest_row = cols
                    break
            
            if manifest_row:
                print("\nActual values in list view:")
                print(f"  Bill of Lading: {manifest_row[0].text.strip()}")
                print(f"  Shipper: {manifest_row[1].text.strip()}")
                print(f"  Consignee: {manifest_row[2].text.strip()}")
                print(f"  Vessel: {manifest_row[3].text.strip()}")
                print(f"  Voyage: {manifest_row[4].text.strip()}")
                
                # Verify the replacements
                print("\nVerifying foreign key replacements:")
                
                shipper_match = manifest_row[1].text.strip() == shipper.name
                print(f"  Shipper name matches: {shipper_match}")
                if not shipper_match:
                    print(f"    Expected: {shipper.name}")
                    print(f"    Found: {manifest_row[1].text.strip()}")
                
                consignee_match = manifest_row[2].text.strip() == consignee.name
                print(f"  Consignee name matches: {consignee_match}")
                if not consignee_match:
                    print(f"    Expected: {consignee.name}")
                    print(f"    Found: {manifest_row[2].text.strip()}")
                
                vessel_match = manifest_row[3].text.strip() == vessel.name
                print(f"  Vessel name matches: {vessel_match}")
                if not vessel_match:
                    print(f"    Expected: {vessel.name}")
                    print(f"    Found: {manifest_row[3].text.strip()}")
                
                voyage_match = manifest_row[4].text.strip() == voyage.name
                print(f"  Voyage name matches: {voyage_match}")
                if not voyage_match:
                    print(f"    Expected: {voyage.name}")
                    print(f"    Found: {manifest_row[4].text.strip()}")
                
                all_match = shipper_match and consignee_match and vessel_match and voyage_match
                print(f"\nAll foreign keys properly replaced: {all_match}")
            else:
                print(f"Error: Could not find manifest {manifest.bill_of_lading} in the list view")
        else:
            print(f"Error: Failed to get manifest list. Status code: {response.status_code}")

if __name__ == '__main__':
    test_foreign_key_names()
