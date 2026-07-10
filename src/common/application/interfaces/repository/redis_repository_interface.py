from abc import ABC, abstractmethod
from typing import Any


class IRedisRepository(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any:
        pass

    @abstractmethod
    async def insert_expires(self, key: str, value: Any, expires_in: int) -> None:
        pass
