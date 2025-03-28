"""
Módulo para gerenciamento de times de heróis na API.

Este módulo contém a rota para criação de times e a definição dos schemas necessários.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Team, SuperHero, TeamHero, User
from app.schemas import TeamCreate, TeamResponse

router = APIRouter(prefix="/teams", tags=["Teams"])
security = HTTPBasic()


@router.post("/", response_model=TeamResponse)
def create_team(team: TeamCreate, credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_session)):
    """Um usuário Líder pode criar um novo time de heróis.

    ### Parâmetros:
    - **team**: Dados do time a ser criado.
    - **db**: Sessão do banco de dados.
    

    ### Retorno:
    - **TeamResponse**: Dados do time criado.

    ### Exceções:
    - **400**: Se um time com o mesmo nome já existir.

    ### Exemplo de JSON de Entrada:
    ```json
        {
            "name": "Vingadores",
            "hero_ids": [1, 2, 3]
        }
    ```
    ## TODO: Corrigir falha de segurança relacionada as credenciais do usuário.
    ## OPTIONAL TODO: Corrigir falha de segurança, pois o usuário pode criar times com ids de heróis que não existem.
    """
    
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not user.is_leader:
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas líderes podem criar times.")
    
    existing_team = db.query(Team).filter(Team.name == team.name).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Time já existe")

    new_team = Team(name=team.name)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    heroes = db.query(SuperHero).filter(SuperHero.id.in_(team.hero_ids)).all()
    for hero in heroes:
        db.add(TeamHero(team_id=new_team.id, hero_id=hero.id))

    db.commit()

    return TeamResponse(id=new_team.id, name=new_team.name, hero_ids=team.hero_ids)
