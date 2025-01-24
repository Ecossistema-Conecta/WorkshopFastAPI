from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase


class ModelBase(DeclarativeBase):
    pass

class SuperHero(ModelBase):
    __tablename__ = "superheroes"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    universe = Column(String)
    real_identity = Column(String)
    power_level = Column(Integer)

    __table_args__ = (UniqueConstraint('name', 'universe', 'real_identity', name="unique_name_universe_real_identity"),)
