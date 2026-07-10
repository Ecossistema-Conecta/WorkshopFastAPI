from datetime import datetime
from typing import cast

from pydantic.types import UUID7

from src.user.domain.models import CreateUserModel, UserModel
from src.user.domain.use_case.user import ICreateUserUseCase


class CreateUserUseCaseSpy(ICreateUserUseCase):
    def __init__(self) -> None:
        pass

    async def execute(self, user: CreateUserModel) -> tuple[str, UserModel]:  # noqa: PLR6301
        mocked_password = user.password if user.password else 'mocked_password'

        mocked_user = UserModel(
            id=cast(UUID7, '019bee48-a59b-7987-83e1-8392b6a5dbc2'),  # pyright: ignore[reportInvalidCast]
            status=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
            name='test',
            email='test@test.com',
            is_superuser=False,
        )
        return mocked_password, mocked_user
