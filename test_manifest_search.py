from app import app
from database import db_session
from generated_models.manifest import Manifest

def test_manifest_search():
    print("\nTesting manifest search functionality...")
    
    with app.test_client() as client:
        # Test numeric search
        print("\nTesting numeric search...")
        response = client.get('/manifest?search=1')
        print(f"Search for '1' status code: {response.status_code}")
        if response.status_code == 200:
            print("Numeric search successful")
        
        # Test text search
        print("\nTesting text search...")
        response = client.get('/manifest?search=BL')
        print(f"Search for 'BL' status code: {response.status_code}")
        if response.status_code == 200:
            print("Text search successful")
        
        # Test empty search
        print("\nTesting empty search...")
        response = client.get('/manifest')
        print(f"Empty search status code: {response.status_code}")
        if response.status_code == 200:
            print("Empty search successful")

if __name__ == '__main__':
    test_manifest_search()
