from typing import Annotated

from fastapi import Depends

from src.common.infra.adapters import HasherAdapter
from src.exceptions.types import ConflictError
from src.user.application.interfaces.cryptography import IHasher
from src.user.application.interfaces.repository import IUserRepository
from src.user.domain.models.user import CreateUserModel, UserModel
from src.user.domain.use_case.user import ICreateUserUseCase
from src.user.infra.repositories import UserRepository


class CreateUserUseCase(ICreateUserUseCase):
    def __init__(
            self,
            repository: Annotated[IUserRepository, Depends(UserRepository)],
            hasher: Annotated[IHasher, Depends(HasherAdapter)]
        ):
        self.__repository = repository
        self.__hasher = hasher

    async def execute(self, user: CreateUserModel) -> tuple[str, UserModel]:
        user_found = await self.__repository.find_user_by_email(email=user.email)

        if user_found:
            raise ConflictError('User already registered')

        temp_password = user.password

        user.password = await self.__hasher.hash(text=temp_password)

        created_user = await self.__repository.create_user(user=user)

        return temp_password, created_user
