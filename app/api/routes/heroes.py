from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from typing import Optional

from app.database import get_session
from app.models import SuperHero, User
from app.schemas import (
    SuperHeroSchema, 
    SuperHeroUpdateSchema, 
    SuperHeroSchemaResponse, 
    SuperHeroSchemaResponseForAny as ResponseForAny,
    SuperHeroSchemaResponseForUserAuthenticated as ResponseForUserAuthenticated,
    SuperHeroSchemaResponseForLeader as ResponseForLeader
)

from app.security.hash_password import HashPassword

router = APIRouter(prefix="/heroes", tags=["Heroes"])
security = HTTPBasic()

async def get_optional_credentials(request: Request) -> Optional[HTTPBasicCredentials]:
    """Retorna as credenciais se forem enviadas, senão retorna None."""
    try:
        return await security(request)
    except Exception:
        return None


@router.post("/")
async def create_hero(data: SuperHeroSchema, db=Depends(get_session)):
    """Cria um novo super-herói.
    
    ### Parâmetros:
    - **name**: Nome do super-herói.
    - **power**: Poder do super-herói.
    - **universe**: Universo do super-herói.
    
    ### Retorno:
    - **SuperHeroSchemaResponse**: Dados do super-herói criado.
    
    ### Exceções:
    - **400**: Se um super-herói com o mesmo nome já existir.
    - **400**: Se o nível de poder for menor que zero.
    
    ### Exemplo de JSON de Entrada: 
    ```json
        {
            "name": "Superman",
            "universe": "DC",
            "real_identity": "Carlos Quente",
            "power_level": "9999"
        }
    ```
    """
    existing_hero = db.query(SuperHero).filter(
        SuperHero.name == data.name,
        SuperHero.universe == data.universe,
        SuperHero.real_identity == data.real_identity
    ).first()
    if existing_hero:
        raise HTTPException(status_code=400, detail="Super-herói já existe")
    if int(data.power_level) < 0:
        raise HTTPException(status_code=400, detail="Nível de poder deve ser maior que zero")
    
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
    """TODO: Implementar autenticação e níveis de acesso para este endpoint.
    
    ### Retorno:
    - **List[SuperHeroSchemaResponse]**: Lista de super-heróis.
    
    ### Exemplo de JSON de Retorno:
        ```json
            [
                {
                    "real_identity": "Carlos Quente",
                    "id": 1,
                    "name": "Superman",
                    "universe": "DC",
                    "power_level": 9999
                },
                {
                    "real_identity": "Bruno Jânio",
                    "id": 2,
                    "name": "Batman",
                    "universe": "DC",
                    "power_level": 9999
                }
            ]
        ```
    """
    heroes = db.query(SuperHero).all()

    return heroes


@router.get("/{id}")
async def get_hero(id: int, credentials: Optional[HTTPBasicCredentials] = Depends(get_optional_credentials), db: Session = Depends(get_session)):
    """Obtém um super-herói específico.
    
    ### Parâmetros:
    - **id**: ID do super-herói a ser obtido.
    
    ### Retorno:
        - **ResponseForAny**: Dados básicos do super-herói.
        - **ResponseForUserAuthenticated**: Dados do super-herói para usuários autenticados.
        - **ResponseForLeader**: Dados do super-herói para líderes.
    
    ### Exceções:
        - **404**: Se o super-herói não for encontrado.
    """
    hero = db.query(SuperHero).filter(SuperHero.id == id).first()
    
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    if credentials:
        if not HashPassword.compair(credentials.password, user.password):
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        user = db.query(User).filter(User.username == credentials.username).first()
        
        if user.is_leader:
            return ResponseForLeader(id=hero.id, name=hero.name, power_level=hero.power_level, universe=hero.universe, real_identity=hero.real_identity)
        
        return ResponseForUserAuthenticated(id=hero.id, name=hero.name, power_level=hero.power_level, universe=hero.universe)
        
    return ResponseForAny(id=hero.id, name=hero.name, power_level=hero.power_level, universe=hero.universe)

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
