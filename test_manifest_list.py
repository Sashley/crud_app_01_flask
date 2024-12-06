from app import app
from database import db_session
from generated_models.manifest import Manifest

def test_manifest_list():
    # Test database query
    print("Testing database query...")
    manifests = Manifest.query.all()
    print(f"Found {len(manifests)} manifests in database")
    if manifests:
        print("\nFirst few manifests:")
        for manifest in manifests[:3]:
            print(f"ID: {manifest.id}, Bill of Lading: {manifest.bill_of_lading}")
    
    # Test template rendering
    print("\nTesting template rendering...")
    with app.test_client() as client:
        response = client.get('/manifest')
        print(f"Response status code: {response.status_code}")
        print(f"Response content length: {len(response.data)}")
        if response.status_code == 200:
            print("Response received successfully")
        else:
            print(f"Error: {response.data.decode('utf-8')}")

if __name__ == '__main__':
    test_manifest_list()
