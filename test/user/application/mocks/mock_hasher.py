from src.user.application.interfaces.cryptography import IHasher


class HasherSpy(IHasher):
    def hash(self, text: str) -> str:  # noqa: PLR6301
        return 'hashed_password'
