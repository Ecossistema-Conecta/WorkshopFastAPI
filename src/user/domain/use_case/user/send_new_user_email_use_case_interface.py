from abc import ABC, abstractmethod

from src.user.domain.models import EmailLogResponseModel, UserModel


class ISendNewUserEmailUseCase(ABC):
    @abstractmethod
    async def execute(self, temp_password: str, user: UserModel) -> EmailLogResponseModel:
        pass
