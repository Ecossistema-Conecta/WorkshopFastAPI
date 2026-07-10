from http import HTTPStatus
from typing import Any

from src.common.presentation.http_types import HttpResponse


def ok(data: Any | None = None) -> HttpResponse:
    return HttpResponse(status_code=HTTPStatus.OK, body=data)


def created() -> HttpResponse:
    return HttpResponse(status_code=HTTPStatus.CREATED, body=None)

def too_many_requests(body: Any) -> HttpResponse:
    return HttpResponse(status_code=HTTPStatus.TOO_MANY_REQUESTS, body=body)
