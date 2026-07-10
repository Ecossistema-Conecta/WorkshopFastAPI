from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.models import SuperHero
from app.schemas import SuperHeroSchema, SuperHeroUpdateSchema


class HeroService:
    def __init__(self):
        self.db: Session | None = None
        self.db_generator = None

    def __enter__(self):
        self.db_generator = get_session()
        self.db = next(self.db_generator)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()

        try:
            next(self.db_generator)
        except StopIteration:
            pass


    def get_hero(self, hero_id: int) -> SuperHero | None:
        return self.db.query(SuperHero).filter(SuperHero.id == hero_id).first()

    def get_all_heroes(self) -> list[SuperHero]:
        return self.db.query(SuperHero).all()

    def create_hero(self, hero_data: SuperHeroSchema) -> SuperHero:
        hero_instance = SuperHero(**hero_data.model_dump())
        self.db.add(hero_instance)
        try:
            self.db.commit()
            self.db.refresh(hero_instance)
            return hero_instance
        except IntegrityError as ie:
            self.db.rollback()
            raise ie

    def update_hero(self, hero_id: int, update_data: SuperHeroUpdateSchema) -> SuperHero | None:
        hero = self.get_hero(hero_id)
        if not hero:
            return None

        hero_data = update_data.model_dump(exclude_unset=True)
        for key, value in hero_data.items():
            if value is not None:
                setattr(hero, key, value)

        self.db.commit()
        self.db.refresh(hero)
        return hero

    def delete_hero(self, hero_id: int) -> bool:
        hero = self.get_hero(hero_id)
        if not hero:
            return False

        self.db.delete(hero)
        self.db.commit()
        return True

