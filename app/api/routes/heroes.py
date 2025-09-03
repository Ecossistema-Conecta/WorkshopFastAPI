from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import IntegrityError

from app.schemas import SuperHeroSchema, SuperHeroUpdateSchema, SuperHeroSchemaResponse
from app.services.heroes import HeroService

router = APIRouter(prefix="/heroes", tags=["Heroes"])


def get_hero_service() -> HeroService:
    with HeroService() as service:
        yield service

@router.post("/", response_model=SuperHeroSchemaResponse)
async def create_hero(
    data: SuperHeroSchema,
    service: HeroService = Depends(get_hero_service)
):
    """Cria um novo Super-Herói."""
    try:
        return service.create_hero(hero_data=data)
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Erro: Herói já existe. {e.orig}")


@router.get("/", response_model=list[SuperHeroSchemaResponse])
async def get_all_heroes(service: HeroService = Depends(get_hero_service)):
    """Retorna todos os Super-Heróis."""
    return service.get_all_heroes()


@router.get("/{id}", response_model=SuperHeroSchemaResponse)
async def get_hero(id: int, service: HeroService = Depends(get_hero_service)):
    """Retorna um Super-Herói específico pelo ID."""
    hero = service.get_hero(hero_id=id)
    if not hero:
        raise HTTPException(status_code=404, detail="Herói não encontrado")
    return hero


@router.put("/{id}", response_model=SuperHeroSchemaResponse)
async def update_hero(
    id: int,
    update_data: SuperHeroUpdateSchema,
    service: HeroService = Depends(get_hero_service)
):
    """Atualiza um Super-Herói."""
    updated_hero = service.update_hero(hero_id=id, update_data=update_data)
    if not updated_hero:
        raise HTTPException(status_code=404, detail="Herói não encontrado")
    return updated_hero


@router.delete("/{id}")
async def delete_hero(id: int, service: HeroService = Depends(get_hero_service)):
    """Deleta um Super-Herói."""
    success = service.delete_hero(hero_id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Herói não encontrado")
    return {"message": "Herói deletado com sucesso"}
