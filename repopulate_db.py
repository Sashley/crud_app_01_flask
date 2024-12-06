import os
from database import db_session, init_db
from init_test_data import init_test_data

def repopulate_database():
    print("Starting database repopulation...")
    
    # Remove existing database files if they exist
    db_files = ['manifest.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"Removed existing database: {db_file}")
            except Exception as e:
                print(f"Error removing {db_file}: {e}")
    
    try:
        # Initialize the database schema
        print("Initializing database schema...")
        init_db()
        
        # Populate with test data
        print("Populating test data...")
        init_test_data()
        
        print("Database repopulation completed successfully!")
        return True
    except Exception as e:
        print(f"Error during database repopulation: {e}")
        return False

if __name__ == "__main__":
    repopulate_database()
