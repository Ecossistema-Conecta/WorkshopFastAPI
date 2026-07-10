from dataclasses import dataclass
from http import HTTPStatus
from random import randint
from unittest.mock import ANY, MagicMock
from uuid import uuid4

import pytest
from _pytest.monkeypatch import MonkeyPatch
from mailersend import Email, EmailBuilder
from pytest_mock.plugin import MockerFixture

from src.common.infra.adapters import MailerAdapter


@pytest.fixture
def mock_mailer_send(mocker: MockerFixture):
    mailer_send_mock = mocker.patch.object(Email, 'send', autospec=True)

    api_response = MagicMock()
    api_response.success = True
    api_response.status_code = 200
    api_response.request_id = str(uuid4())
    api_response.rate_limit_remaining = randint(1, 100)
    api_response.retry_after = None

    mailer_send_mock.return_value = api_response

    return mailer_send_mock, api_response


@dataclass
class SutTypes:
    sut: MailerAdapter


@pytest.fixture
def make_sut() -> SutTypes:
    sut = MailerAdapter()

    return SutTypes(sut=sut)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_return_a_response_with_success_equal_true(
    make_sut: SutTypes, monkeypatch: MonkeyPatch, mock_mailer_send: MagicMock
) -> None:
    sut = make_sut.sut
    _, api_response = mock_mailer_send  # pyright: ignore[reportUnknownVariableType]

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    response = await sut.send_email(
        sender_email='project_admin@mail.com',
        sender_name='admin',
        receiver_email='random_guy@mail.com',
        receiver_name='random_guy',
        subject='Test email',
        content='Test content',
    )

    assert response.email_id == api_response.request_id  # pyright: ignore[reportUnknownMemberType]
    assert response.success == api_response.success  # pyright: ignore[reportUnknownMemberType]
    assert response.status_code == HTTPStatus(api_response.status_code)  # pyright: ignore[reportUnknownMemberType]
    assert response.rate_limit_remaining == api_response.rate_limit_remaining  # pyright: ignore[reportUnknownMemberType]
    assert response.retry_after == api_response.retry_after  # pyright: ignore[reportUnknownMemberType]
    assert response.error_message is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_call_from_email_with_correct_params(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    from_email_spy = mocker.spy(EmailBuilder, 'from_email')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    await sut.send_email(**mocked_send_mail_properties)

    from_email_spy.assert_called_once_with(
        ANY, email=mocked_send_mail_properties['sender_email'], name=mocked_send_mail_properties['sender_name']
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_raise_if_from_email_raises(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    from_email_mock = mocker.patch.object(EmailBuilder, 'from_email', autospec=True)
    from_email_mock.side_effect = Exception('Test exception')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    with pytest.raises(Exception):  # noqa: PT011
        await sut.send_email(**mocked_send_mail_properties)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_call_to_method_with_correct_params(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    to_spy = mocker.spy(EmailBuilder, 'to')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    await sut.send_email(**mocked_send_mail_properties)

    to_spy.assert_called_once_with(
        ANY, email=mocked_send_mail_properties['receiver_email'], name=mocked_send_mail_properties['receiver_name']
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_raise_if_to_method_raises(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    to_mock = mocker.patch.object(EmailBuilder, 'to', autospec=True)
    to_mock.side_effect = Exception('Test exception')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    with pytest.raises(Exception):  # noqa: PT011
        await sut.send_email(**mocked_send_mail_properties)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_call_subject_with_correct_params(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    subject_spy = mocker.spy(EmailBuilder, 'subject')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    await sut.send_email(**mocked_send_mail_properties)

    subject_spy.assert_called_once_with(ANY, subject=mocked_send_mail_properties['subject'])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_raise_if_subject_raises(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    subject_mock = mocker.patch.object(EmailBuilder, 'subject', autospec=True)
    subject_mock.side_effect = Exception('Test exception')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    with pytest.raises(Exception):  # noqa: PT011
        await sut.send_email(**mocked_send_mail_properties)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_call_html_method_with_correct_params(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    html_spy = mocker.spy(EmailBuilder, 'html')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    await sut.send_email(**mocked_send_mail_properties)

    html_spy.assert_called_once_with(ANY, html_content=mocked_send_mail_properties['content'])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_raise_if_html_method_raises(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    html_mock = mocker.patch.object(EmailBuilder, 'html', autospec=True)
    html_mock.side_effect = Exception('Test exception')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    with pytest.raises(Exception):  # noqa: PT011
        await sut.send_email(**mocked_send_mail_properties)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_raise_if_build_method_raises(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    build_mock = mocker.patch.object(EmailBuilder, 'build', autospec=True)
    build_mock.side_effect = Exception('Test exception')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    with pytest.raises(Exception):  # noqa: PT011
        await sut.send_email(**mocked_send_mail_properties)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_call_send_method_with_correct_params(
    make_sut: SutTypes, mocker: MockerFixture, monkeypatch: MonkeyPatch, mock_mailer_send: MagicMock
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    build_mock = mocker.patch.object(EmailBuilder, 'build', autospec=True)
    build_response = MagicMock()
    build_mock.return_value = build_response

    mailer_send_mock, _ = mock_mailer_send  # pyright: ignore[reportUnknownVariableType]

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    await sut.send_email(**mocked_send_mail_properties)

    mailer_send_mock.assert_called_once_with(ANY, email=build_response)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_raise_if_send_method_raises(
    make_sut: SutTypes,
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    mock_mailer_send: MagicMock,  # pyright: ignore[reportUnusedParameter]
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    mailer_send_mock, _ = mock_mailer_send  # pyright: ignore[reportUnknownVariableType]
    mailer_send_mock.side_effect = Exception('Test exception')

    mocked_send_mail_properties = {
        'sender_email': 'project_admin@mail.com',
        'sender_name': 'admin',
        'receiver_email': 'random_guy@mail.com',
        'receiver_name': 'random_guy',
        'subject': 'Test email',
        'content': 'Test content',
    }

    with pytest.raises(Exception):  # noqa: PT011
        await sut.send_email(**mocked_send_mail_properties)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_email_method_should_return_a_response_with_success_equal_false(
    make_sut: SutTypes, monkeypatch: MonkeyPatch, mocker: MockerFixture
) -> None:
    sut = make_sut.sut

    monkeypatch.setenv('MAILERSEND_API_KEY', 'fake_key')

    mailer_send_mock = mocker.patch.object(Email, 'send', autospec=True)

    api_response = MagicMock()
    api_response.success = False
    api_response.status_code = 500
    api_response.request_id = None
    api_response.rate_limit_remaining = 0
    api_response.retry_after = None
    api_response.data = {'message': 'Any error'}

    mailer_send_mock.return_value = api_response

    response = await sut.send_email(
        sender_email='project_admin@mail.com',
        sender_name='admin',
        receiver_email='random_guy@mail.com',
        receiver_name='random_guy',
        subject='Test email',
        content='Test content',
    )

    assert response.email_id == api_response.request_id
    assert response.success == api_response.success
    assert response.status_code == HTTPStatus(api_response.status_code)
    assert response.rate_limit_remaining == api_response.rate_limit_remaining
    assert response.retry_after == api_response.retry_after
    assert response.error_message == api_response.data.get('message')
