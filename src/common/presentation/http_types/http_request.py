from typing import Any

from pydantic import BaseModel


class HttpRequest(BaseModel):
    method: str
    body: dict[Any, Any] | None = None
    headers: dict[Any, Any] | None = None
    query_params: dict[Any, Any] | None = None
    path_params: dict[Any, Any] | None = None
    url: str | None = None
    ipv4: str | None = None
    form: dict[Any, Any] | None = None
