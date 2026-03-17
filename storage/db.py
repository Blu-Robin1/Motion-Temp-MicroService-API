import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load DB config
with open('../config/storage_config.yml', 'r') as f:
    app_config = yaml.safe_load(f)

db_user = app_config['datastore']['user']
db_password = app_config['datastore']['password']
db_hostname = app_config['datastore']['hostname']
db_port = app_config['datastore']['port']
db_name = app_config['datastore']['db']

# Format connection string
connection_string = (
    f"mysql://{db_user}:{db_password}@"
    f"{db_hostname}:{db_port}/{db_name}"
)

ENGINE = create_engine(connection_string)
Session = sessionmaker(bind=ENGINE)

def make_session():
    return Session()
