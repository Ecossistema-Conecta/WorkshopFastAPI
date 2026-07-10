from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.services.heroes import HeroService
from app.schemas import SuperHeroSchema, SuperHeroUpdateSchema


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


class UpdateHeroInput(BaseModel):
    hero_id: int = Field(
        description="ID do herói que será editado. Este campo é obrigatório."
    )
    name: Optional[str] = Field(
        default=None,
        description="Novo nome público do herói."
    )
    real_identity: Optional[str] = Field(
        default=None,
        description="Nova identidade secreta do herói."
    )
    power_level: Optional[int] = Field(
        default=None,
        description="Novo nível de poder do herói."
    )
    universe: Optional[str] = Field(
        default=None,
        description="Novo universo do herói."
    )

@tool("update_hero", args_schema=UpdateHeroInput)
def update_hero(hero_id: int, name: str | None = None, real_identity: str | None = None, universe: str | None = None, power_level: int | None = None) -> str:
    """
    Atualiza os detalhes de um Super-Herói existente e retorna uma mensagem de confirmação.
    Use esta ferramenta para modificar os atributos de um herói já registrado, fornecendo o ID do herói e os campos a serem atualizados.
    """
    try:
        with HeroService() as service:
            update_data = SuperHeroUpdateSchema(
                name=name,
                real_identity=real_identity,
                universe=universe,
                power_level=power_level
            )
            updated_hero = service.update_hero(hero_id=hero_id, update_data=update_data)
            if updated_hero:
                return f"Herói com ID {hero_id} atualizado com sucesso."
            else:
                return f"Herói com ID {hero_id} não encontrado."

    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"


class DeleteHeroInput(BaseModel):
    hero_id: int = Field(
        description="ID do herói que será excluído."
    )

@tool("delete_hero", args_schema=DeleteHeroInput)
def delete_hero(hero_id: int) -> str:
    """
    Exclui um Super-Herói existente e retorna uma mensagem de confirmação.
    Use esta ferramenta para remover um herói do banco de dados, fornecendo o ID do herói a ser excluído.
    """
    try:
        with HeroService() as service:
            success = service.delete_hero(hero_id=hero_id)
            if success:
                return f"Herói com ID {hero_id} excluído com sucesso."
            else:
                return f"Herói com ID {hero_id} não encontrado."

    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"

class ListHeroesInput(BaseModel):
    pass

@tool("list_heroes_power_level", args_schema=ListHeroesInput)
def list_heroes_power_level() -> str:
    """
    Lista todos os heróis e seus níveis de poder.
    Use esta ferramenta para obter uma visão geral dos heróis registrados e seus respectivos níveis de poder.
    """
    try:
        with HeroService() as service:
            heroes = service.get_all_heroes()
            if not heroes:
                return "Nenhum herói encontrado."

            response_lines = ["Lista de Heróis e seus Níveis de Poder:"]
            for hero in heroes:
                response_lines.append(f"- {hero.name} (ID: {hero.id}): Nível de Poder {hero.power_level}")

            return "\n".join(response_lines)

    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"

tools = [create_hero, update_hero, delete_hero, list_heroes_power_level]

