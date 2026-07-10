from dataclasses import dataclass
from uuid import UUID, uuid4, uuid7

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.infra.entities import EmailLog
from src.common.infra.repositories import EmailLogRepository
from src.user.infra.entities import User


@pytest.fixture
def make_user(session: AsyncSession, mock_db_fields):
    async def _make_user(name: str = 'test name', email: str = 'test@test.com') -> UUID:
        new_user = User(name=name, email=email, password='Secure_password123')

        with mock_db_fields(model=User, id=uuid7()) as (id, time):
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

        return id

    return _make_user


@dataclass
class SutTypes:
    sut: EmailLogRepository


@pytest.fixture
def make_sut(session: AsyncSession) -> SutTypes:
    sut = EmailLogRepository(session)

    return SutTypes(sut=sut)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_send_new_user_email_log_should_return_an_uuid_on_success(make_sut: SutTypes, mock_db_fields, make_user):
    sut = make_sut.sut

    sender = await make_user(name='sender', email='sender@mail.com')
    receiver = await make_user(name='receiver', email='receiver@mail.com')
    id_control = str(uuid4())
    subject = 'Test email'
    body = 'Test email'
    error = None

    with mock_db_fields(model=EmailLog) as (id, time):
        new_email_log_id = await sut.create_send_new_user_email_log(
            id_control=id_control, receiver_id=receiver, sender_id=sender, subject=subject, body=body, error=error
        )

    assert isinstance(new_email_log_id, UUID)
    assert new_email_log_id == id
