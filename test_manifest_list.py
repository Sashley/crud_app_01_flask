from app import app
from database import db_session
from generated_models.manifest import Manifest
from generated_models.client import Client
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from generated_models.port import Port
from generated_models.user import User
from datetime import datetime
import json

def test_manifest_list():
    """Test the manifest list functionality"""
    print("\n=== Testing Manifest List ===")
    
    # Test database query
    print("\nTesting database query...")
    manifests = db_session.query(Manifest).all()
    print(f"Found {len(manifests)} manifests in database")
    if manifests:
        print("\nFirst few manifests:")
        for manifest in manifests[:3]:
            print(f"ID: {manifest.id}, Bill of Lading: {manifest.bill_of_lading}")
    
    # Test template rendering with related entities
    print("\nTesting template rendering...")
    with app.test_client() as client:
        response = client.get('/manifest')
        print(f"Response status code: {response.status_code}")
        print(f"Response content length: {len(response.data)}")
        if response.status_code == 200:
            print("Response received successfully")
            # Check if related entity names are in the response
            content = response.data.decode('utf-8')
            if manifests and manifests[0].shipper:
                assert manifests[0].shipper.name in content, "Shipper name not found in response"
            if manifests and manifests[0].vessel:
                assert manifests[0].vessel.name in content, "Vessel name not found in response"
        else:
            print(f"Error: {response.data.decode('utf-8')}")

def test_manifest_form_create():
    """Test the manifest creation form"""
    print("\n=== Testing Manifest Creation ===")
    
    # First, get some valid IDs for the form
    client = db_session.query(Client).first()
    vessel = db_session.query(Vessel).first()
    voyage = db_session.query(Voyage).first()
    port = db_session.query(Port).first()
    user = db_session.query(User).first()
    
    if not all([client, vessel, voyage, port, user]):
        print("Warning: Missing required related entities for testing")
        return
    
    test_data = {
        'bill_of_lading': 'TEST-BOL-001',
        'shipper_id': str(client.id),
        'consignee_id': str(client.id),
        'vessel_id': str(vessel.id),
        'voyage_id': str(voyage.id),
        'port_of_loading_id': str(port.id),
        'port_of_discharge_id': str(port.id),
        'place_of_delivery': 'Test Delivery Place',
        'place_of_receipt': 'Test Receipt Place',
        'clauses': 'Test Clauses',
        'date_of_receipt': '2024-01-01',
        'manifester_id': str(user.id)
    }
    
    with app.test_client() as client:
        # Test GET request (form display)
        print("\nTesting form display...")
        response = client.get('/manifest/new')
        assert response.status_code == 200, "Failed to get create form"
        content = response.data.decode('utf-8')
        
        # Verify dropdowns are present
        assert 'shipper_id' in content, "Shipper dropdown not found"
        assert 'vessel_id' in content, "Vessel dropdown not found"
        assert 'date_of_receipt' in content, "Date input not found"
        
        # Test POST request (form submission)
        print("\nTesting form submission...")
        response = client.post('/manifest/new', data=test_data)
        assert response.status_code in [200, 302], f"Form submission failed with status {response.status_code}"
        
        # Verify the manifest was created
        manifest = db_session.query(Manifest).filter_by(bill_of_lading='TEST-BOL-001').first()
        assert manifest is not None, "Manifest was not created"
        assert manifest.date_of_receipt is not None, "Date was not saved"
        print(f"Created manifest ID: {manifest.id}")

def test_manifest_form_edit():
    """Test the manifest edit form"""
    print("\n=== Testing Manifest Edit ===")
    
    # Get an existing manifest
    manifest = db_session.query(Manifest).first()
    if not manifest:
        print("No manifest found for testing edit")
        return
    
    print(f"\nTesting edit for manifest ID: {manifest.id}")
    
    with app.test_client() as client:
        # Test GET request (form display)
        print("\nTesting edit form display...")
        response = client.get(f'/manifest/{manifest.id}/edit')
        assert response.status_code == 200, "Failed to get edit form"
        content = response.data.decode('utf-8')
        
        # Verify form is populated
        assert manifest.bill_of_lading in content, "Bill of lading not populated"
        if manifest.shipper:
            assert manifest.shipper.name in content, "Shipper not selected"
        
        # Test POST request (form submission)
        print("\nTesting edit form submission...")
        test_data = {
            'bill_of_lading': manifest.bill_of_lading + '-EDITED',
            'shipper_id': str(manifest.shipper_id if manifest.shipper_id else ''),
            'consignee_id': str(manifest.consignee_id if manifest.consignee_id else ''),
            'vessel_id': str(manifest.vessel_id if manifest.vessel_id else ''),
            'voyage_id': str(manifest.voyage_id if manifest.voyage_id else ''),
            'port_of_loading_id': str(manifest.port_of_loading_id if manifest.port_of_loading_id else ''),
            'port_of_discharge_id': str(manifest.port_of_discharge_id if manifest.port_of_discharge_id else ''),
            'place_of_delivery': manifest.place_of_delivery or '',
            'place_of_receipt': manifest.place_of_receipt or '',
            'clauses': manifest.clauses or '',
            'date_of_receipt': '2024-02-01',
            'manifester_id': str(manifest.manifester_id if manifest.manifester_id else '')
        }
        
        response = client.post(f'/manifest/{manifest.id}/edit', data=test_data)
        assert response.status_code in [200, 302], f"Form submission failed with status {response.status_code}"
        
        # Verify the changes were saved
        updated_manifest = db_session.query(Manifest).get(manifest.id)
        assert updated_manifest.bill_of_lading.endswith('-EDITED'), "Changes were not saved"
        assert updated_manifest.date_of_receipt is not None, "Date was not saved"
        print("Edit successful")

def run_all_tests():
    """Run all manifest tests"""
    try:
        test_manifest_list()
        test_manifest_form_create()
        test_manifest_form_edit()
        print("\nAll tests completed successfully!")
    except AssertionError as e:
        print(f"\nTest failed: {str(e)}")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
    finally:
        # Clean up test data
        try:
            test_manifest = db_session.query(Manifest).filter_by(bill_of_lading='TEST-BOL-001').first()
            if test_manifest:
                db_session.delete(test_manifest)
                db_session.commit()
        except:
            db_session.rollback()

if __name__ == '__main__':
    run_all_tests()
