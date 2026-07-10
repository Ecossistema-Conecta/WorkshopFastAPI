from abc import ABC, abstractmethod

from src.user.domain.models.user import CreateUserModel, UserModel


class IUserRepository(ABC):
    @abstractmethod
    async def find_user_by_email(self, email: str) -> UserModel | None:
        pass

    @abstractmethod
    async def create_user(self, user: CreateUserModel) -> UserModel:
        pass
