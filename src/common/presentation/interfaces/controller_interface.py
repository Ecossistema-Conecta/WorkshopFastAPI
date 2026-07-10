from abc import ABC, abstractmethod

from src.common.presentation.http_types import HttpRequest, HttpResponse


class IController(ABC):
    @abstractmethod
    async def handle(self, http_request: HttpRequest) -> HttpResponse:
        pass
