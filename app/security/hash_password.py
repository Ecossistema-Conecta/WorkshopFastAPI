import bcrypt

class HashPassword:
  @staticmethod
  def hash(password: str) -> str:
    """Gera o hash da senha utilizando bcrypt com salt automaticamente gerado."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

  @staticmethod
  def compair(password: str, hashed_password: str) -> bool:
    """Compara a senha fornecida com o hash armazenado."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
