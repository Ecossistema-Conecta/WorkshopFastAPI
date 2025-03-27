from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str
    password: str
    
class UserSchemaResponse(BaseModel):
    """Schema de resposta para o usuário.
    ### Campos:
    - **id**: ID do usuário.
    - **username**: Nome de usuário.
    - **is_leader**: Indica se o usuário é líder.
    """
    id: int
    username: str
    is_leader: bool


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