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
