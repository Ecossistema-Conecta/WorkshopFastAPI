from datetime import datetime
from typing import cast

from pydantic.types import UUID7

from src.user.application.interfaces.repository import IUserRepository
from src.user.domain.models.user import CreateUserModel, UserModel


class UserRepositorySpy(IUserRepository):
    async def find_user_by_email(self, email: str) -> UserModel | None:  # noqa: PLR6301
        return UserModel(
            id=cast(UUID7, '019bee48-a59b-7987-83e1-8392b6a5dbc2'),  # pyright: ignore[reportInvalidCast]
            status=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
            name='test',
            email='test@test.com',
            is_superuser=False,
        )  # type: ignore

    async def create_user(self, user: CreateUserModel) -> UserModel:  # noqa: PLR6301
        return UserModel(
            id=cast(UUID7, '019bee48-a59b-7987-83e1-8392b6a5dbc2'),  # pyright: ignore[reportInvalidCast]
            status=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
            name='test',
            email='test@test.com',
            is_superuser=False,
        )  # type: ignore
