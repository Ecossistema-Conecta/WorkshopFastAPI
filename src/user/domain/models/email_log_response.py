from http import HTTPStatus
from uuid import UUID

from pydantic import BaseModel


class EmailLogResponseModel(BaseModel):
    success: bool
    status_code: HTTPStatus
    log_id: UUID | None = None
    error_message: str | None = None
    retry_after: int | None = None
