from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.main.config import get_session
from src.user.application.interfaces.repository import IUserRepository
from src.user.domain.models import CreateUserModel, UserModel
from src.user.infra.entities import User


class UserRepository(IUserRepository):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.__session = session

    async def create_user(self, user: CreateUserModel) -> UserModel:
        new_user = User(name=user.name, email=user.email, password=user.password)

        self.__session.add(new_user)
        await self.__session.commit()
        await self.__session.refresh(new_user)

        created_user = UserModel.model_validate(new_user)

        return created_user

    async def find_user_by_email(self, email: str) -> UserModel | None:
        user = await self.__session.scalar(select(User).where(User.email == email))

        if not user:
            return None

        return UserModel.model_validate(user)
