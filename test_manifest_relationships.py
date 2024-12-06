from app import app
from database import db_session
from generated_models.manifest import Manifest
import logging

logging.basicConfig(level=logging.DEBUG)

def test_manifest_relationships():
    print("\nTesting manifest relationships and search...")
    
    with app.test_client() as client:
        # Test searching by bill of lading
        print("\nTesting bill of lading search...")
        response = client.get('/manifest?search=BL001')
        print(f"Search for 'BL001' status code: {response.status_code}")
        
        # Test searching by shipper name
        print("\nTesting shipper name search...")
        response = client.get('/manifest?search=Shipper')
        print(f"Search for 'Shipper' status code: {response.status_code}")
        
        # Test searching by vessel name
        print("\nTesting vessel name search...")
        response = client.get('/manifest?search=Vessel')
        print(f"Search for 'Vessel' status code: {response.status_code}")
        
        # Test searching by voyage number
        print("\nTesting voyage number search...")
        response = client.get('/manifest?search=V001')
        print(f"Search for 'V001' status code: {response.status_code}")

if __name__ == '__main__':
    test_manifest_relationships()
