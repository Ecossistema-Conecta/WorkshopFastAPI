from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from app.services.heroes import HeroService
from app.schemas import SuperHeroSchema

class CreateHeroInput(BaseModel):
    name: str = Field(description="O nome público do herói. Este campo é obrigatório.")
    real_identity: str = Field(description="A identidade secreta do herói (seu nome de civil). Este campo é obrigatório.")
    power_level: int = Field(description="O nível de poder do heroi, em número. Este campo é obrigatório.")
    universe: str = Field(description="O universo daquele heroi. Este campo é obrigatório.")

@tool("create_hero", args_schema=CreateHeroInput)
def create_hero(name: str, real_identity: str, universe: str, power_level: int) -> str:
    """
    Cria um novo Super-Herói e retorna uma mensagem de confirmação incluindo o ID único do herói criado.
    Use esta ferramenta para registrar um novo herói com todos os seus detalhes.
    """
    try:
        with HeroService() as service:
            hero_data = SuperHeroSchema(
                name=name,
                real_identity=real_identity,
                universe=universe,
                power_level=power_level
            )
            created_hero = service.create_hero(hero_data=hero_data)
            return f"Herói '{created_hero.name}' criado com sucesso com ID: {created_hero.id}."

    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"

tools = [create_hero]

