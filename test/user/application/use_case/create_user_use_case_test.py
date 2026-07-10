from dataclasses import dataclass
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from pydantic.types import UUID
from pytest_mock import MockerFixture

from src.exceptions.types.conflict import ConflictError
from src.user.application.use_case.user import CreateUserUseCase
from src.user.domain.models import UserModel
from src.user.domain.models.user import CreateUserModel
from test.user.application.mocks.mock_hasher import HasherSpy
from test.user.application.mocks.mock_user_repository import UserRepositorySpy


def user_factory() -> CreateUserModel:
    new_user = CreateUserModel(name='test name', email='test@test.com', password='Secure_password123')

    return new_user


def get_repository_path() -> str:
    return 'test.user.application.mocks.mock_user_repository.UserRepositorySpy'


def get_hasher_path() -> str:
    return 'test.user.application.mocks.mock_hasher.HasherSpy'


@dataclass
class SutTypes:
    sut: CreateUserUseCase
    repository: UserRepositorySpy
    hasher: HasherSpy


@pytest.fixture
def make_sut() -> SutTypes:
    hasher = HasherSpy()
    repository = UserRepositorySpy()
    sut = CreateUserUseCase(repository=repository, hasher=hasher)

    return SutTypes(sut=sut, repository=repository, hasher=hasher)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_return_success_message(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    new_user = user_factory()
    temp_password = new_user.password

    mocker.patch(
        f'{get_repository_path()}.find_user_by_email',
        new_callable=AsyncMock,
        return_value=None,
    )

    returned_password, returned_user = await sut.execute(user=new_user)

    assert isinstance(returned_password, str)
    assert returned_password == temp_password
    assert isinstance(returned_user, UserModel)
    assert hasattr(returned_user, 'id')
    assert isinstance(returned_user.id, UUID)
    assert hasattr(returned_user, 'status')
    assert isinstance(returned_user.status, bool)
    assert hasattr(returned_user, 'created_at')
    assert isinstance(returned_user.created_at, datetime)
    assert hasattr(returned_user, 'updated_at')
    assert isinstance(returned_user.updated_at, datetime)
    assert hasattr(returned_user, 'name')
    assert isinstance(returned_user.name, str)
    assert hasattr(returned_user, 'email')
    assert isinstance(returned_user.email, str)
    assert hasattr(returned_user, 'is_superuser')
    assert isinstance(returned_user.is_superuser, bool)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_should_call_find_user_by_email_with_correct_param(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    repository = make_sut.repository
    new_user = user_factory()

    mocker.patch(
        f'{get_repository_path()}.find_user_by_email',
        new_callable=AsyncMock,
        return_value=None,
    )

    find_user_by_email_spy = mocker.spy(repository, 'find_user_by_email')

    await sut.execute(new_user)

    find_user_by_email_spy.assert_called_once_with(email=new_user.email)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_should_raise_exception_when_find_user_by_email_raise_exception(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    new_user = user_factory()

    mocker.patch(
        f'{get_repository_path()}.find_user_by_email',
        side_effect=Exception('Test exception'),
    )

    with pytest.raises(Exception):  # noqa: PT011
        await sut.execute(user=new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_raise_conflict_exception_when_user_already_exists(make_sut: SutTypes) -> None:
    sut = make_sut.sut
    new_user = user_factory()

    with pytest.raises(ConflictError):
        await sut.execute(user=new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_hash_with_correct_param(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    hasher = make_sut.hasher
    new_user = user_factory()
    password = new_user.password

    mocker.patch(
        f'{get_repository_path()}.find_user_by_email',
        new_callable=AsyncMock,
        return_value=None,
    )

    hash_spy = mocker.spy(hasher, 'hash')

    await sut.execute(new_user)

    hash_spy.assert_called_once_with(text=password)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_should_raise_exception_when_hash_raise_exception(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    new_user = user_factory()

    mocker.patch(
        f'{get_repository_path()}.find_user_by_email',
        new_callable=AsyncMock,
        return_value=None,
    )

    mocker.patch(
        f'{get_hasher_path()}.hash',
        side_effect=Exception('Test exception'),
    )

    with pytest.raises(Exception):  # noqa: PT011
        await sut.execute(user=new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_create_user_with_correct_param(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    repository = make_sut.repository
    new_user = user_factory()

    mocker.patch(
        f'{get_repository_path()}.find_user_by_email',
        new_callable=AsyncMock,
        return_value=None,
    )

    create_user_spy = mocker.spy(repository, 'create_user')

    await sut.execute(new_user)

    create_user_spy.assert_called_once_with(user=new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_should_raise_exception_when_create_user_raise_exception(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    new_user = user_factory()

    mocker.patch(
        f'{get_repository_path()}.find_user_by_email',
        new_callable=AsyncMock,
        return_value=None,
    )

    mocker.patch(
        f'{get_repository_path()}.create_user',
        side_effect=Exception('Test exception'),
    )

    with pytest.raises(Exception):  # noqa: PT011
        await sut.execute(user=new_user)
