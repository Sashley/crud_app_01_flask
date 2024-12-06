from app import app
from database import db_session
from generated_models.manifest import Manifest
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG)

def extract_search_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    rows = soup.find_all('tr')[1:]  # Skip header row
    for row in rows:
        cols = row.find_all('td')
        if cols:
            result = {
                'bill_of_lading': cols[0].text.strip(),
                'shipper': cols[1].text.strip(),
                'consignee': cols[2].text.strip()
            }
            results.append(result)
    return results

def test_incremental_search():
    print("\nTesting incremental search functionality...")
    
    with app.test_client() as client:
        # Test incremental bill of lading search
        print("\nTesting incremental bill of lading search...")
        search_term = "BL001"
        for i in range(1, len(search_term) + 1):
            partial = search_term[:i]
            print(f"\n=== Incrementally searching for '{partial}': ===")
            response = client.get(f'/manifest?search={partial}')
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                results = extract_search_results(response.data.decode())
                print(f"Found {len(results)} results:")
                for result in results:
                    print(f"  • {result['bill_of_lading']}")
                    print(f"    Shipper: {result['shipper']}")
                    print(f"    Consignee: {result['consignee']}")
        
        # Test incremental shipper name search
        print("\nTesting incremental shipper name search...")
        search_term = "Cargo"
        for i in range(1, len(search_term) + 1):
            partial = search_term[:i]
            print(f"\n=== Incrementally searching for '{partial}': ===")
            response = client.get(f'/manifest?search={partial}')
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                results = extract_search_results(response.data.decode())
                print(f"Found {len(results)} results:")
                for result in results:
                    print(f"  • {result['bill_of_lading']}")
                    print(f"    Shipper: {result['shipper']}")
                    print(f"    Consignee: {result['consignee']}")

if __name__ == '__main__':
    test_incremental_search()
