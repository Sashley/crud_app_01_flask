from database import db_session
from generated_models.manifest import Manifest
from generated_models.lineitem import LineItem

def check_relationships():
    print("\nChecking Manifest-LineItem Relationships...")
    
    # Get all manifests
    manifests = db_session.query(Manifest).all()
    print(f"\nTotal Manifests: {len(manifests)}")
    
    # Get all line items
    line_items = db_session.query(LineItem).all()
    print(f"Total Line Items: {len(line_items)}")
    
    # Check each manifest's line items
    for manifest in manifests[:5]:  # Check first 5 manifests
        print(f"\nManifest ID: {manifest.id}")
        print(f"BOL: {manifest.bill_of_lading}")
        
        # Get line items directly from database
        direct_items = db_session.query(LineItem).filter(LineItem.manifest_id == manifest.id).all()
        print(f"Direct line items query count: {len(direct_items)}")
        
        # Get line items through relationship
        relationship_items = manifest.line_items
        print(f"Relationship line items count: {len(relationship_items)}")
        
        # Print details of line items
        if direct_items:
            print("\nLine Items:")
            for item in direct_items:
                print(f"  ID: {item.id}")
                print(f"  Description: {item.description}")
                print(f"  Manifest ID: {item.manifest_id}")

if __name__ == '__main__':
    check_relationships()
