from fastapi import APIRouter

from app.api.routes import teams, heroes, users

api_router = APIRouter()
api_router.include_router(teams.router)
api_router.include_router(heroes.router)
api_router.include_router(users.router)
