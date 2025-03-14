from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import os

engine = create_engine(os.getenv("DATABASE_URL"))

def get_session() -> Session:
    with sessionmaker(bind=engine)() as session:
        yield session
