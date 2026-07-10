from http import HTTPStatus

from pydantic import BaseModel


class MailerAdapterResponse(BaseModel):
    email_id: str | None
    success: bool
    status_code: HTTPStatus
    rate_limit_remaining: int
    retry_after: int | None
    error_message: str | None
