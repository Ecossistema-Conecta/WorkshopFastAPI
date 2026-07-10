from dataclasses import dataclass

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.domain.models import CreateUserModel, UserModel
from src.user.infra.entities import User
from src.user.infra.repositories import UserRepository


def user_factory() -> CreateUserModel:
    new_user = CreateUserModel(name='test name', email='test@test.com', password='Secure_password123')

    return new_user


@dataclass
class SutTypes:
    sut: UserRepository


@pytest.fixture
def make_sut(session: AsyncSession) -> SutTypes:
    sut = UserRepository(session)

    return SutTypes(sut=sut)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user_should_return_user_model_on_success(make_sut: SutTypes, mock_db_fields):
    sut = make_sut.sut
    new_user = user_factory()

    with mock_db_fields(model=User) as (id, time):
        user = await sut.create_user(user=new_user)

    assert isinstance(user, UserModel)
    assert user.model_dump() == {
        'id': id,
        'status': True,
        'created_at': time,
        'updated_at': time,
        'name': 'test name',
        'email': 'test@test.com',
        'is_superuser': False,
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_user_by_email_should_return_user_model_on_success(make_sut: SutTypes, mock_db_fields):
    sut = make_sut.sut
    new_user = user_factory()

    with mock_db_fields(model=User) as (id, time):
        await sut.create_user(user=new_user)

    user = await sut.find_user_by_email(email=new_user.email)

    assert isinstance(user, UserModel)
    assert user.model_dump() == {
        'id': id,
        'status': True,
        'created_at': time,
        'updated_at': time,
        'name': 'test name',
        'email': 'test@test.com',
        'is_superuser': False,
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_user_by_email_should_return_none_if_user_is_not_found(make_sut: SutTypes, mock_db_fields):
    sut = make_sut.sut
    new_user = user_factory()

    user = await sut.find_user_by_email(email=new_user.email)

    assert user is None
