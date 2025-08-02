from sqlalchemy import create_engine # database connection setup
from sqlalchemy.orm import declarative_base, sessionmaker # object-relational mapping setup

DATABASE_URL = "sqlite:///stokvel.db" # SQLite database URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # create connection for SQLite
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def init_db(): # function to initialize the database
    from models_logic import Group, Member, Contribution, Payout, Goal
    Base.metadata.create_all(bind=engine) 