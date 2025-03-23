from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import yaml

with open("/app/conf/storage_config.yml", 'r') as file:
    app_config = yaml.safe_load(file)

# Extract values from the loaded configuration
db_user = app_config['datastore']['user']
db_password = app_config['datastore']['password']
db_hostname = app_config['datastore']['hostname']
db_name = app_config['datastore']['db']
db_port = app_config['datastore']['port']

connection_string = f"mysql://{db_user}:{db_password}@{db_hostname}:{db_port}/{db_name}"

engine = create_engine(connection_string)

# Function to create and return a session
def make_session():
    session = sessionmaker(bind=engine)()
    session.execute(text("SET time_zone = 'America/Los_Angeles'"))
    return session
