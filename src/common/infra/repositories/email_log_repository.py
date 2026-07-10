from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.application.interfaces.repository import IEmailLogRepository
from src.common.domain.models import EmailLogModel
from src.common.infra.entities import EmailLog
from src.main.config import get_session


class EmailLogRepository(IEmailLogRepository):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.__session = session

    async def create_send_new_user_email_log(
        self, id_control: str | None, receiver_id: UUID, sender_id: UUID | None, subject: str, body: str, error: str | None
    ) -> UUID:
        new_email_log = EmailLog(
            id_control=id_control, receiver_id=receiver_id, sender_id=sender_id, subject=subject, body=body, error=error
        )

        self.__session.add(new_email_log)
        await self.__session.commit()
        await self.__session.refresh(new_email_log)

        created_email_log = EmailLogModel.model_validate(new_email_log)

        return created_email_log.id
