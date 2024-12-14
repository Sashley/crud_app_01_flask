from database import db_session
from sqlalchemy import func
from generated_models.client import Client
from generated_models.commodity import Commodity
from generated_models.containerstatus import ContainerStatus
from generated_models.country import Country
from generated_models.packtype import PackType
from generated_models.port import Port
from generated_models.shippingcompany import ShippingCompany
from generated_models.user import User

def verify_counts():
    print("\nVerifying record counts:")
    print(f"Clients: {db_session.query(func.count(Client.id)).scalar()}/300")
    print(f"Commodities: {db_session.query(func.count(Commodity.id)).scalar()}/50")
    print(f"Container Statuses: {db_session.query(func.count(ContainerStatus.id)).scalar()}/15")
    print(f"Countries: {db_session.query(func.count(Country.id)).scalar()}/20")
    print(f"Pack Types: {db_session.query(func.count(PackType.id)).scalar()}/40")
    print(f"Ports: {db_session.query(func.count(Port.id)).scalar()}/20")
    print(f"Shipping Companies: {db_session.query(func.count(ShippingCompany.id)).scalar()}/3")
    print(f"Users: {db_session.query(func.count(User.id)).scalar()}/5")

def verify_sample_data():
    print("\nVerifying sample data:")
    
    print("\nSample Client:")
    client = db_session.query(Client).first()
    print(f"Name: {client.name}")
    print(f"Email: {client.email}")
    print(f"Country: {client.country.name if client.country else 'No country'}")
    
    print("\nSample Commodity:")
    commodity = db_session.query(Commodity).first()
    print(f"Name: {commodity.name}")
    print(f"Description: {commodity.description}")
    
    print("\nSample Container Status:")
    status = db_session.query(ContainerStatus).first()
    print(f"Name: {status.name}")
    print(f"Description: {status.description}")
    
    print("\nSample Port:")
    port = db_session.query(Port).first()
    print(f"Name: {port.name}")
    print(f"Prefix: {port.prefix}")
    print(f"Country: {port.country.name if port.country else 'No country'}")
    
    print("\nSample Shipping Company:")
    company = db_session.query(ShippingCompany).first()
    print(f"Name: {company.name}")

if __name__ == '__main__':
    try:
        verify_counts()
        verify_sample_data()
    except Exception as e:
        print(f"Error verifying data: {str(e)}")
    finally:
        db_session.close()
