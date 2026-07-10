from http import HTTPStatus
from random import randint
from unittest.mock import MagicMock
from uuid import uuid4

from mailersend import EmailBuilder, MailerSendClient

from src.common.application.interfaces.adapters import IMailerAdapter
from src.common.domain.models import MailerAdapterResponse


class MailerAdapter(IMailerAdapter):
    @staticmethod
    async def send_email(
        sender_email: str, sender_name: str, receiver_email: str, receiver_name: str, subject: str, content: str
    ) -> MailerAdapterResponse:
        email_id = None
        rate_limit_remaining = 0
        error_message = None

        email = (
            EmailBuilder()
            .from_email(email=sender_email, name=sender_name)
            .to(email=receiver_email, name=receiver_name)
            .subject(subject=subject)
            .html(html_content=content)
            .build()
        )

        mailer_send_client = MailerSendClient()
        # response = mailer_send_client.emails.send(email=email)
        api_response = MagicMock()
        api_response.success = True
        api_response.status_code = 200
        api_response.request_id = str(uuid4())
        api_response.rate_limit_remaining = randint(1, 100)
        api_response.retry_after = None
        response = api_response

        status_code = response.status_code

        if response.success:
            email_id = response.request_id
            rate_limit_remaining = response.rate_limit_remaining if response.rate_limit_remaining else 0
        else:
            data = response.data
            error_message = data.get('message', 'Unknown error')

        return MailerAdapterResponse(
            email_id=email_id,
            success=response.success,
            status_code=HTTPStatus(status_code),
            rate_limit_remaining=rate_limit_remaining,
            retry_after=response.retry_after,
            error_message=error_message,
        )
