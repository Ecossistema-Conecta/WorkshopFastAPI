from http import HTTPStatus
from typing import Any

from pydantic import BaseModel


class HttpResponse(BaseModel):
    body: Any
    status_code: HTTPStatus
