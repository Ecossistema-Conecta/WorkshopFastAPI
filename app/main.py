import os
from sqlalchemy.exc import IntegrityError

from fastapi import FastAPI, Depends, HTTPException
from fastapi import FastAPI


from app.models import ModelBase, SuperHero
from app.schemas import SuperHeroSchema, SuperHeroUpdateSchema, SuperHeroSchemaResponse

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

app = FastAPI()

engine = create_engine(os.getenv("DATABASE_URL"))
ModelBase.metadata.create_all(bind=engine)


def get_session() -> Session:
    with sessionmaker(bind=engine)() as session:
        yield session


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/heroes/")
async def create_hero(data: SuperHeroSchema, db = Depends(get_session)):
    hero_data = data.model_dump()
    hero_instance = SuperHero(**hero_data)

    db.add(hero_instance)
    try:
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        return {"error": str(ie.orig)}

    db.refresh(hero_instance)

    return hero_instance

@app.get("/heroes/")
async def get_all_heroes(db = Depends(get_session)):
    heroes = db.query(SuperHero).all()

    return heroes

@app.get("/heroes/{id}", response_model=SuperHeroSchemaResponse)
async def get_hero(id: int, db = Depends(get_session)):
    hero = db.query(SuperHero).filter(SuperHero.id == id).first()

    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    return hero

@app.put("/heroes/{id}")
async def update_hero(id: int, update_data: SuperHeroUpdateSchema, db = Depends(get_session)):
    hero = db.query(SuperHero).filter(SuperHero.id == id).first()
    hero_data = update_data.model_dump(exclude_unset=True)

    if hero:
        db.query(SuperHero).filter(SuperHero.id == id).update(hero_data, synchronize_session="fetch")
    else:
        raise HTTPException(status_code=404, detail="Hero not found")

    db.commit()

    db.refresh(hero)

    return hero

@app.delete("/heroes/{id}")
async def delete_hero(id: int, db = Depends(get_session)):
    hero = db.query(SuperHero).filter(SuperHero.id == id).first()

    if hero:
        db.delete(hero)
        db.commit()

    return {"message": "Hero deleted"}
