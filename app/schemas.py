from pydantic import BaseModel


class SuperHeroSchema(BaseModel):
    name: str
    universe: str
    real_identity: str
    power_level: int


class SuperHeroUpdateSchema(BaseModel):
    name: str | None = None
    universe: str | None = None
    real_identity: str | None = None
    power_level: int | None = None


class SuperHeroSchemaResponse(BaseModel):
    name: str | None = None
    universe: str
    real_identity: str


class TeamCreate(BaseModel):
    name: str
    hero_ids: list[int]


class TeamResponse(BaseModel):
    id: int
    name: str
    hero_ids: list[int]


class TeamResponseFull(BaseModel):
    id: int
    name: str
    heroes: list[SuperHeroSchemaResponse]