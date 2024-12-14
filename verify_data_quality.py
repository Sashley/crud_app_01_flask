from sqlalchemy import func
from database import db_session
from generated_models.client import Client
from generated_models.commodity import Commodity
from generated_models.container import Container
from generated_models.manifest import Manifest
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from generated_models.port import Port
from generated_models.lineitem import LineItem
from generated_models.packtype import PackType
from generated_models.user import User
from generated_models.containerstatus import ContainerStatus
from generated_models.shippingcompany import ShippingCompany

def verify_data():
    """Verify generated data"""
    try:
        print("\nVerifying generated data...")
        
        # Check record counts
        print("\nRecord counts:")
        counts = {
            'Clients': db_session.query(Client).count(),
            'Commodities': db_session.query(Commodity).count(),
            'Containers': db_session.query(Container).count(),
            'Manifests': db_session.query(Manifest).count(),
            'Vessels': db_session.query(Vessel).count(),
            'Voyages': db_session.query(Voyage).count(),
            'Ports': db_session.query(Port).count(),
            'Line Items': db_session.query(LineItem).count(),
            'Pack Types': db_session.query(PackType).count(),
            'Users': db_session.query(User).count(),
            'Container Statuses': db_session.query(ContainerStatus).count(),
            'Shipping Companies': db_session.query(ShippingCompany).count()
        }
        
        for entity, count in counts.items():
            print(f"{entity}: {count}")
        
        # Check relationships
        print("\nChecking relationships:")
        
        # Calculate average line items per manifest
        total_manifests = counts['Manifests']
        total_line_items = counts['Line Items']
        if total_manifests > 0:
            avg_items = total_line_items / total_manifests
            print(f"Average line items per manifest: {avg_items:.2f}")
        
        # Manifests without line items
        orphan_manifests = db_session.query(Manifest)\
            .outerjoin(LineItem)\
            .group_by(Manifest.id)\
            .having(func.count(LineItem.id) == 0)\
            .count()
        print(f"Manifests without line items: {orphan_manifests}")
        
        # Check seasonal patterns
        print("\nChecking seasonal patterns:")
        monthly_volumes = db_session.query(
            func.extract('month', Manifest.date_of_receipt).label('month'),
            func.sum(LineItem.quantity).label('total_quantity')
        ).join(LineItem)\
         .group_by('month')\
         .order_by('month')\
         .all()
        
        if monthly_volumes:
            print("Monthly shipping volumes:")
            for month, quantity in monthly_volumes:
                print(f"Month {int(month)}: {int(quantity):,} units")
        else:
            print("No monthly volume data found")
        
        # Check weight distribution
        print("\nChecking weight distribution:")
        weight_stats = db_session.query(
            func.min(LineItem.weight).label('min_weight'),
            func.avg(LineItem.weight).label('avg_weight'),
            func.max(LineItem.weight).label('max_weight')
        ).first()
        
        if weight_stats:
            print(f"Weight distribution (kg):")
            print(f"  Minimum: {weight_stats.min_weight:,.0f}")
            print(f"  Average: {weight_stats.avg_weight:,.0f}")
            print(f"  Maximum: {weight_stats.max_weight:,.0f}")
        
        # Check container utilization
        print("\nChecking container utilization:")
        container_status_counts = db_session.query(
            ContainerStatus.name,
            func.count(Container.id)
        ).join(Container)\
         .group_by(ContainerStatus.name)\
         .all()
        
        if container_status_counts:
            print("Container status distribution:")
            for status, count in container_status_counts:
                print(f"  {status}: {count}")
        
        print("\nVerification complete.")
        
    except Exception as e:
        print(f"Error verifying data: {str(e)}")
    finally:
        db_session.close()

if __name__ == '__main__':
    verify_data()
