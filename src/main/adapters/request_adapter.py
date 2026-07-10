from typing import Any, Callable
from fastapi import Request
from fastapi.responses import JSONResponse

from src.common.presentation.http_types import HttpRequest, HttpResponse


async def request_adapter(request: Request, controller_handler: Callable, parsed_body: Any = None) -> JSONResponse:
    body = parsed_body
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        try:
            body = await request.json()
        except Exception:
            body = None

    http_request = HttpRequest(
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        path_params=request.path_params,
        body=body,
        url=str(request.url),
        ipv4=request.client.host if request.client else None,
        method=request.method,
    )

    http_response: HttpResponse = await controller_handler(http_request)
    return JSONResponse(content=http_response.body, status_code=http_response.status_code)
