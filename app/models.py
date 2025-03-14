from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class ModelBase(DeclarativeBase):
    pass


class TeamHero(ModelBase):
    __tablename__ = "team_heroes"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    hero_id = Column(Integer, ForeignKey("superheroes.id"), nullable=False)

    team = relationship("Team", back_populates="team_heroes")
    hero = relationship("SuperHero", back_populates="hero_teams")


class SuperHero(ModelBase):
    __tablename__ = "superheroes"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    universe = Column(String)
    real_identity = Column(String)
    power_level = Column(Integer)

    hero_teams = relationship("TeamHero", back_populates="hero")

    __table_args__ = (UniqueConstraint('name', 'universe', 'real_identity', name="unique_name_universe_real_identity"),)


class Team(ModelBase):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    team_heroes = relationship("TeamHero", back_populates="team")
