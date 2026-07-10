from abc import ABC, abstractmethod

from src.user.domain.models import CreateUserModel, UserModel


class ICreateUserUseCase(ABC):
    @abstractmethod
    async def execute(self, user: CreateUserModel) -> tuple[str, UserModel]:
        pass
