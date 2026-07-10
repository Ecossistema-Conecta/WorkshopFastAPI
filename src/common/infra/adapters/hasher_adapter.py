import bcrypt

from src.user.application.interfaces.cryptography import IHasher


class HasherAdapter(IHasher):
    async def hash(self, text: str) -> str:
        binary_text = text.encode('ascii')
        __salt = bcrypt.gensalt()

        hashed_text = bcrypt.hashpw(binary_text, __salt)

        return hashed_text.decode('utf-8')
