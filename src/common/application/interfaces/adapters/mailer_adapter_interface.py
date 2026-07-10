from abc import ABC, abstractmethod

from src.common.domain.models import MailerAdapterResponse


class IMailerAdapter(ABC):
    @staticmethod
    @abstractmethod
    async def send_email(
        sender_email: str, sender_name: str, receiver_email: str, receiver_name: str, subject: str, content: str
    ) -> MailerAdapterResponse:
        pass
