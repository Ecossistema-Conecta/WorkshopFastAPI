from abc import ABC, abstractmethod


class IHasher(ABC):
    @abstractmethod
    def hash(self, text: str) -> str:
        pass
