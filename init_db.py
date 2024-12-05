from database import init_db, engine, Base
from generator.output.models import Manifest, Client, Vessel, Voyage, Port, User

if __name__ == '__main__':
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully.")
