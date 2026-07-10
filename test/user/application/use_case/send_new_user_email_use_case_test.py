from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from random import randint
from unittest.mock import AsyncMock
from uuid import UUID, uuid4, uuid7

import pytest
from pytest_mock import MockerFixture

from src.common.application.interfaces.adapters import IMailerAdapter
from src.common.application.interfaces.repository import IEmailLogRepository, IRedisRepository
from src.common.domain.models import EmailCacheKeys, MailerAdapterResponse
from src.main.config.settings import settings
from src.user.application.use_case.user import SendNewUserEmailUseCase
from src.user.domain.models import EmailLogResponseModel, UserModel


def user_factory() -> UserModel:
    new_user = UserModel(
        id=uuid7(),
        status=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
        name='test',
        email='test@test.com',
        is_superuser=False,
    )

    return new_user


def send_mail_return_factory(
    success: bool = True,
    status_code: HTTPStatus = HTTPStatus.OK,
    rate_limit_remaining: int = randint(1, 100),
    retry_after: int = randint(1, 1000),
    error_message: str | None = None,
):
    response = MailerAdapterResponse(
        email_id=str(uuid4()),
        success=success,
        status_code=status_code,
        rate_limit_remaining=rate_limit_remaining,
        retry_after=retry_after,
        error_message=error_message,
    )

    return response


@dataclass
class SutTypes:
    sut: SendNewUserEmailUseCase
    email_log_repository_spy: IEmailLogRepository | AsyncMock
    mailer_adapter_spy: IMailerAdapter | AsyncMock
    redis_repository_spy: IRedisRepository | AsyncMock


@pytest.fixture
def make_sut() -> SutTypes:
    email_log_repository_spy = AsyncMock()
    mailer_adapter_spy = AsyncMock()
    redis_repository_spy = AsyncMock()
    sut = SendNewUserEmailUseCase(
        email_log_repository=email_log_repository_spy, mailer_adapter=mailer_adapter_spy, redis_repository=redis_repository_spy
    )

    return SutTypes(
        sut=sut,
        email_log_repository_spy=email_log_repository_spy,
        mailer_adapter_spy=mailer_adapter_spy,
        redis_repository_spy=redis_repository_spy,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_return_success_true_in_email_log_response_model(make_sut: SutTypes) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = None  # pyright: ignore[reportAttributeAccessIssue]
    mailer_adapter_spy.send_email.return_value = send_mail_return_factory()  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]

    new_user = user_factory()
    temp_password = 'temp_password'

    result = await sut.execute(temp_password=temp_password, user=new_user)

    assert isinstance(result, EmailLogResponseModel)
    assert result.success is True
    assert isinstance(result.log_id, UUID)
    assert result.status_code == HTTPStatus.OK


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_insert_expires_with_correct_params_if_rate_limit_count_equals_zero(
    make_sut: SutTypes, mocker: MockerFixture
) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    key = EmailCacheKeys.EMAIL_RATE_LIMIT_QUOTA.value

    redis_repository_spy.get.return_value = 0  # pyright: ignore[reportAttributeAccessIssue]
    insert_expires_spy = mocker.spy(redis_repository_spy, 'insert_expires')
    in_seconds = 30
    sut.calc_expires = AsyncMock(return_value=in_seconds)

    new_user = user_factory()
    temp_password = 'temp_password'

    await sut.execute(temp_password=temp_password, user=new_user)

    insert_expires_spy.assert_called_once_with(key=key, value=0, expires_in=in_seconds)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_raise_if_insert_expires_raises(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy

    redis_repository_spy.get.return_value = 0  # pyright: ignore[reportAttributeAccessIssue]
    redis_repository_spy.insert_expires.side_effect = Exception('Test exception')  # pyright: ignore[reportAttributeAccessIssue]

    new_user = user_factory()
    temp_password = 'temp_password'

    with pytest.raises(Exception):  # noqa: PT011
        await sut.execute(temp_password=temp_password, user=new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_return_success_false_in_email_log_response_model_if_rate_limit_count_equals_zero(
    make_sut: SutTypes,
) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy

    redis_repository_spy.get.return_value = 0  # pyright: ignore[reportAttributeAccessIssue]

    new_user = user_factory()
    temp_password = 'temp_password'

    result = await sut.execute(temp_password=temp_password, user=new_user)

    assert isinstance(result, EmailLogResponseModel)
    assert result.success is False
    assert result.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert result.error_message == 'Rate limit exceeded'
    assert result.retry_after is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_send_new_user_email_with_correct_params(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_adapter_spy.send_email.return_value = send_mail_return_factory()  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    send_new_user_email_spy = mocker.spy(sut, 'send_new_user_email')

    new_user = user_factory()
    temp_password = 'temp_password'

    await sut.execute(temp_password=temp_password, user=new_user)

    send_new_user_email_spy.assert_called_once_with(temp_password=temp_password, new_user=new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_get_first_access_email_with_correct_params(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_adapter_spy.send_email.return_value = send_mail_return_factory()  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    get_first_access_email_spy = mocker.spy(sut, 'get_first_access_email')

    new_user = user_factory()
    temp_password = 'temp_password'

    await sut.execute(temp_password=temp_password, user=new_user)

    get_first_access_email_spy.assert_called_once_with(temp_password=temp_password)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_raise_if_get_first_access_email_raises(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_adapter_spy.send_email.return_value = send_mail_return_factory()  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    get_first_access_email_spy = mocker.spy(sut, 'get_first_access_email')
    get_first_access_email_spy.side_effect = Exception('Test exception')

    new_user = user_factory()
    temp_password = 'temp_password'

    with pytest.raises(Exception):  # noqa: PT011
        await sut.execute(temp_password=temp_password, user=new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_send_email_with_correct_params(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_adapter_spy.send_email.return_value = send_mail_return_factory()  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    send_email_spy = mocker.spy(mailer_adapter_spy, 'send_email')

    new_user = user_factory()
    temp_password = 'temp_password'
    content = await sut.get_first_access_email(temp_password=temp_password)

    await sut.execute(temp_password=temp_password, user=new_user)

    send_email_spy.assert_called_once_with(
        sender_email=settings.DEFAULT_EMAIL,
        sender_name=settings.PROJECT_NAME,
        receiver_email=new_user.email,
        receiver_name=new_user.name,
        subject='Bem vindo(a) ao Projeto',
        content=content,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_raise_if_send_email_raises(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_adapter_spy.send_email.return_value = send_mail_return_factory()  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    send_email_spy = mocker.spy(mailer_adapter_spy, 'send_email')
    send_email_spy.side_effect = Exception('Test exception')

    new_user = user_factory()
    temp_password = 'temp_password'

    with pytest.raises(Exception):  # noqa: PT011
        await sut.execute(temp_password=temp_password, user=new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_insert_expires_with_correct_params_if_response_status_code_equals_429(
    make_sut: SutTypes, mocker: MockerFixture
) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy
    key = EmailCacheKeys.EMAIL_RATE_LIMIT_QUOTA.value

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_response = send_mail_return_factory(success=False, status_code=HTTPStatus.TOO_MANY_REQUESTS, rate_limit_remaining=0)
    mailer_adapter_spy.send_email.return_value = mailer_response  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    insert_expires_spy = mocker.spy(redis_repository_spy, 'insert_expires')
    in_seconds = 30
    sut.calc_expires = AsyncMock(return_value=in_seconds)

    new_user = user_factory()
    temp_password = 'temp_password'

    await sut.execute(temp_password=temp_password, user=new_user)

    insert_expires_spy.assert_called_once_with(key=key, value=mailer_response.rate_limit_remaining, expires_in=in_seconds)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_create_send_new_user_email_log_with_correct_params_if_response_status_code_equals_429(
    make_sut: SutTypes, mocker: MockerFixture
) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_response = send_mail_return_factory(success=False, status_code=HTTPStatus.TOO_MANY_REQUESTS, rate_limit_remaining=0)
    mailer_adapter_spy.send_email.return_value = mailer_response  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    create_send_new_user_email_log_spy = mocker.spy(email_log_repository_spy, 'create_send_new_user_email_log')

    new_user = user_factory()
    temp_password = 'temp_password'
    content = await sut.get_first_access_email(temp_password=temp_password)

    await sut.execute(temp_password=temp_password, user=new_user)

    create_send_new_user_email_log_spy.assert_called_once_with(
        id_control=mailer_response.email_id,
        receiver_id=new_user.id,
        sender_id=None,
        subject='Bem vindo(a) ao Projeto',
        body=content,
        error='Rate limit exceeded',
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_raise_if_create_send_new_user_email_log_raises(make_sut: SutTypes, mocker: MockerFixture) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_response = send_mail_return_factory(success=False, status_code=HTTPStatus.TOO_MANY_REQUESTS, rate_limit_remaining=0)
    mailer_adapter_spy.send_email.return_value = mailer_response  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.side_effect = Exception(
        'Test exception'
    )  # pyright: ignore[reportAttributeAccessIssue]

    new_user = user_factory()
    temp_password = 'temp_password'

    with pytest.raises(Exception):  # noqa: PT011
        await sut.execute(temp_password=temp_password, user=new_user)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_return_success_false_in_email_log_response_model_if_response_status_code_equals_429(
    make_sut: SutTypes,
) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_response = send_mail_return_factory(success=False, status_code=HTTPStatus.TOO_MANY_REQUESTS, rate_limit_remaining=0)
    mailer_adapter_spy.send_email.return_value = mailer_response  # pyright: ignore[reportFunctionMemberAccess]
    log_id = uuid7()
    email_log_repository_spy.create_send_new_user_email_log.return_value = log_id  # pyright: ignore[reportAttributeAccessIssue]

    new_user = user_factory()
    temp_password = 'temp_password'

    result = await sut.execute(temp_password=temp_password, user=new_user)

    assert isinstance(result, EmailLogResponseModel)
    assert result.success is False
    assert result.log_id == log_id
    assert result.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert result.error_message == 'Rate limit exceeded'
    assert result.retry_after is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_create_send_new_user_email_log_with_correct_params_if_response_success_equals_false(
    make_sut: SutTypes, mocker: MockerFixture
) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_response = send_mail_return_factory(
        success=False, status_code=HTTPStatus.INTERNAL_SERVER_ERROR, rate_limit_remaining=0, error_message='Internal Server Error'
    )
    mailer_adapter_spy.send_email.return_value = mailer_response  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    create_send_new_user_email_log_spy = mocker.spy(email_log_repository_spy, 'create_send_new_user_email_log')

    new_user = user_factory()
    temp_password = 'temp_password'
    content = await sut.get_first_access_email(temp_password=temp_password)

    await sut.execute(temp_password=temp_password, user=new_user)

    create_send_new_user_email_log_spy.assert_called_once_with(
        id_control=mailer_response.email_id,
        receiver_id=new_user.id,
        sender_id=None,
        subject='Bem vindo(a) ao Projeto',
        body=content,
        error=mailer_response.error_message,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_return_success_false_in_email_log_response_model_if_response_success_equals_false(
    make_sut: SutTypes,
) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_response = send_mail_return_factory(
        success=False, status_code=HTTPStatus.INTERNAL_SERVER_ERROR, rate_limit_remaining=0, error_message='Internal Server Error'
    )
    mailer_adapter_spy.send_email.return_value = mailer_response  # pyright: ignore[reportFunctionMemberAccess]
    log_id = uuid7()
    email_log_repository_spy.create_send_new_user_email_log.return_value = log_id  # pyright: ignore[reportAttributeAccessIssue]

    new_user = user_factory()
    temp_password = 'temp_password'

    result = await sut.execute(temp_password=temp_password, user=new_user)

    assert isinstance(result, EmailLogResponseModel)
    assert result.success is False
    assert result.log_id == log_id
    assert result.status_code == mailer_response.status_code
    assert result.error_message == mailer_response.error_message
    assert result.retry_after is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_insert_expires_with_correct_params_if_response_success_equals_true(
    make_sut: SutTypes, mocker: MockerFixture
) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy
    key = EmailCacheKeys.EMAIL_RATE_LIMIT_QUOTA.value

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_response = send_mail_return_factory()
    mailer_adapter_spy.send_email.return_value = mailer_response  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    insert_expires_spy = mocker.spy(redis_repository_spy, 'insert_expires')
    in_seconds = 30
    sut.calc_expires = AsyncMock(return_value=in_seconds)

    new_user = user_factory()
    temp_password = 'temp_password'

    await sut.execute(temp_password=temp_password, user=new_user)

    insert_expires_spy.assert_called_once_with(key=key, value=mailer_response.rate_limit_remaining, expires_in=in_seconds)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_should_call_create_send_new_user_email_log_with_correct_params_if_response_success_equals_true(
    make_sut: SutTypes, mocker: MockerFixture
) -> None:
    sut = make_sut.sut
    redis_repository_spy = make_sut.redis_repository_spy
    mailer_adapter_spy = make_sut.mailer_adapter_spy
    email_log_repository_spy = make_sut.email_log_repository_spy

    redis_repository_spy.get.return_value = randint(1, 100)  # pyright: ignore[reportAttributeAccessIssue]
    mailer_response = send_mail_return_factory()
    mailer_adapter_spy.send_email.return_value = mailer_response  # pyright: ignore[reportFunctionMemberAccess]
    email_log_repository_spy.create_send_new_user_email_log.return_value = uuid7()  # pyright: ignore[reportAttributeAccessIssue]
    create_send_new_user_email_log_spy = mocker.spy(email_log_repository_spy, 'create_send_new_user_email_log')

    new_user = user_factory()
    temp_password = 'temp_password'
    content = await sut.get_first_access_email(temp_password=temp_password)

    await sut.execute(temp_password=temp_password, user=new_user)

    create_send_new_user_email_log_spy.assert_called_once_with(
        id_control=mailer_response.email_id,
        receiver_id=new_user.id,
        sender_id=None,
        subject='Bem vindo(a) ao Projeto',
        body=content,
        error=None,
    )
