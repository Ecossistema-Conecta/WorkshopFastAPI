from abc import ABC, abstractmethod
from uuid import UUID


class IEmailLogRepository(ABC):
    @abstractmethod
    async def create_send_new_user_email_log(
        self, id_control: str | None, receiver_id: UUID, sender_id: UUID | None, subject: str, body: str, error: str | None
    ) -> UUID:
        pass
