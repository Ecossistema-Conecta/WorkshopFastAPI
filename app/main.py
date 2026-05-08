import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.main import api_router
from app.database import engine
from app.models import ModelBase


@asynccontextmanager
async def lifespan(app: FastAPI):
    ModelBase.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.include_router(api_router)
