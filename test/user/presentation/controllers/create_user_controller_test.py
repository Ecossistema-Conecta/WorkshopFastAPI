from dataclasses import dataclass
from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from src.common.presentation.http_types import HttpRequest, HttpResponse
from src.user.domain.models.user import CreateUserModel
from src.user.domain.use_case.user import ISendNewUserEmailUseCase
from src.user.presentation.controllers import CreateUserController
from test.user.presentation.mocks.mock_create_user_use_case import CreateUserUseCaseSpy


def make_http_request(method: str) -> HttpRequest:
    body = {
        'name': 'test name',
        'email': 'test@test.com',
        'password': 'Secure_password123',
    }

    return HttpRequest(method=method, body=body)


def get_create_user_use_case_path() -> str:
    return 'test.user.presentation.mocks.mock_create_user_use_case.CreateUserUseCaseSpy.execute'


def get_send_new_user_email_use_case_path() -> str:
    return 'test.user.presentation.mocks.mock_send_new_user_email_use_case.SendNewUserEmailUseCaseSpy.execute'


@dataclass
class SutTypes:
    sut: CreateUserController
    create_user_use_case: CreateUserUseCaseSpy
    send_new_user_email_use_case: ISendNewUserEmailUseCase | AsyncMock


@pytest.fixture
def make_sut() -> SutTypes:
    create_user_use_case = CreateUserUseCaseSpy()
    send_new_user_email_use_case = AsyncMock()
    sut = CreateUserController(
        create_user_use_case=create_user_use_case, send_new_user_email_use_case=send_new_user_email_use_case
    )

    return SutTypes(sut=sut, create_user_use_case=create_user_use_case, send_new_user_email_use_case=send_new_user_email_use_case)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_should_return_created_status(make_sut: SutTypes) -> None:
    sut = make_sut.sut
    request = make_http_request(method='POST')

    response = await sut.handle(request)

    assert isinstance(response, HttpResponse)
    assert response.body is None
    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_should_call_create_user_use_case_with_correct_params(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    create_user_use_case = make_sut.create_user_use_case
    request = make_http_request(method='POST')
    new_user = CreateUserModel(**request.body)  # pyright: ignore[reportCallIssue]

    execute_spy = mocker.spy(create_user_use_case, 'execute')

    await sut.handle(request)

    execute_spy.assert_called_once_with(new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_should_raise_exception_when_create_user_use_case_raise_exception(
    make_sut: SutTypes, mocker: MockerFixture
) -> None:
    sut = make_sut.sut
    request = make_http_request(method='POST')

    mocker.patch(get_create_user_use_case_path(), side_effect=Exception('Test exception'))

    with pytest.raises(Exception):  # noqa: PT011
        await sut.handle(request)
