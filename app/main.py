import os

from fastapi import FastAPI


from app.models import ModelBase

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

app = FastAPI()

engine = create_engine(os.getenv("DATABASE_URL"))
ModelBase.metadata.create_all(bind=engine)


def get_session() -> Session:
    with sessionmaker(bind=engine)() as session:
        yield session


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
