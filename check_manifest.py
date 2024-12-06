from database import db_session
from generated_models.manifest import Manifest

manifests = Manifest.query.all()
print(f"Total manifests: {len(manifests)}")
if manifests:
    print("\nFirst few manifests:")
    for manifest in manifests[:3]:
        print(f"ID: {manifest.id}, Bill of Lading: {manifest.bill_of_lading}")
