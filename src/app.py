from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI

from src.main.config import register_routes


@asynccontextmanager
async def lifespan(application: FastAPI):
    register_routes(application)
    yield

app = FastAPI(lifespan=lifespan)

if __name__ == '__main__':
    uvicorn.run(
        app='src.app:app',
        host='0.0.0.0',
        port=8000,
        log_level='debug',
        reload=True,
    )
