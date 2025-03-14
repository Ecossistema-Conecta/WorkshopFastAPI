from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.models import SuperHero
from app.schemas import SuperHeroSchema, SuperHeroUpdateSchema, SuperHeroSchemaResponse

router = APIRouter(prefix="/heroes", tags=["Heroes"])

@router.post("/")
async def create_hero(data: SuperHeroSchema, db=Depends(get_session)):
    """Crie-me"""
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


@router.get("/")
async def get_all_heroes(db=Depends(get_session)):
    heroes = db.query(SuperHero).all()

    return heroes


@router.get("/{id}", response_model=SuperHeroSchemaResponse)
async def get_hero(id: int, db=Depends(get_session)):
    hero = db.query(SuperHero).filter(SuperHero.id == id).first()

    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    return hero


@router.put("/{id}")
async def update_hero(id: int, update_data: SuperHeroUpdateSchema, db=Depends(get_session)):
    hero = db.query(SuperHero).filter(SuperHero.id == id).first()
    hero_data = update_data.model_dump(exclude_unset=True)

    if hero:
        db.query(SuperHero).filter(SuperHero.id == id).update(hero_data, synchronize_session="fetch")
    else:
        raise HTTPException(status_code=404, detail="Hero not found")

    db.commit()

    db.refresh(hero)

    return hero


@router.delete("/{id}")
async def delete_hero(id: int, db=Depends(get_session)):
    hero = db.query(SuperHero).filter(SuperHero.id == id).first()

    if hero:
        db.delete(hero)
        db.commit()

    return {"message": "Hero deleted"}
