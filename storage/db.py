from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ENGINE = create_engine("mysql://pyro:cynical@localhost/slop")

def make_session():
    return sessionmaker(bind=ENGINE)()