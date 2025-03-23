from models import Base
from db import engine
from sqlalchemy import inspect

# Function to drop and create tables automatically
def drop_and_create_tables():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # If tables exist, drop them
    if existing_tables:
        Base.metadata.drop_all(engine)
        print(f"Dropped existing tables: {existing_tables}")
    
    # Create new tables
    Base.metadata.create_all(engine)
    print("Tables created successfully")

def create_tables_if_not_exist():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Only create the tables if they don't already exist
    if not existing_tables:
        Base.metadata.create_all(engine)
        print("Tables created successfully")
    else:
        print("Tables already exist. No changes made.")

if __name__ == "__main__":
    create_tables_if_not_exist()
